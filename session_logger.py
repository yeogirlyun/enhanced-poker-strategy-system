# filename: session_logger.py
"""
Hold'em Session Logger & Analytics System

REVISION HISTORY:
================

Version 1.0 (2025-01-25) - Initial Implementation
- Created SQLite database schema for session tracking
- Implemented SessionLogger class for decision logging
- Added comprehensive decision data capture including:
  * Hand context (hole cards, board, position, stack sizes)
  * Action details (user action, optimal action, timing)
  * Game state (pot size, betting history, street)
- Implemented mistake classification and severity assessment
- Added SessionAnalyzer for performance analytics
- Created pattern recognition for common mistake types
- Implemented trend analysis and improvement suggestions

Features:
- Persistent SQLite database storage
- Detailed decision logging with full context
- Advanced analytics and pattern recognition
- Performance trend analysis over time
- Mistake categorization and severity scoring
- Comprehensive reporting system
- Command-line interface for data analysis
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

class SessionLogger:
    def __init__(self, db_path='holdem_sessions.db'):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            total_hands INTEGER,
            total_decisions INTEGER,
            correct_decisions INTEGER,
            accuracy REAL,
            strategy_version TEXT
        )
        ''')
        
        # Decisions table - detailed log of every decision
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS decisions (
            decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            hand_number INTEGER,
            street TEXT,
            position TEXT,
            is_ip BOOLEAN,
            hole_cards TEXT,
            board_cards TEXT,
            pot_size REAL,
            to_call REAL,
            stack_size REAL,
            preflop_hs INTEGER,
            postflop_hs INTEGER,
            hand_rank TEXT,
            action_history TEXT,
            was_pfa BOOLEAN,
            user_action TEXT,
            user_size REAL,
            optimal_action TEXT,
            optimal_size REAL,
            is_correct BOOLEAN,
            decision_time REAL,
            timestamp TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
        ''')
        
        # Mistakes table - focused on errors for quick analysis
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mistakes (
            mistake_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            decision_id INTEGER,
            mistake_type TEXT,
            street TEXT,
            position TEXT,
            severity TEXT,
            description TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id),
            FOREIGN KEY (decision_id) REFERENCES decisions (decision_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_session(self, strategy_version="1.0"):
        """Start a new training session."""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO sessions (session_id, start_time, strategy_version)
        VALUES (?, ?, ?)
        ''', (session_id, datetime.now(), strategy_version))
        
        conn.commit()
        conn.close()
        return session_id
    
    def log_decision(self, session_id, decision_data):
        """Log a single decision with full context."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO decisions (
            session_id, hand_number, street, position, is_ip,
            hole_cards, board_cards, pot_size, to_call, stack_size,
            preflop_hs, postflop_hs, hand_rank, action_history, was_pfa,
            user_action, user_size, optimal_action, optimal_size, is_correct,
            decision_time, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, decision_data['hand_number'], decision_data['street'],
            decision_data['position'], decision_data['is_ip'],
            decision_data['hole_cards'], decision_data['board_cards'],
            decision_data['pot_size'], decision_data['to_call'], decision_data['stack_size'],
            decision_data['preflop_hs'], decision_data['postflop_hs'],
            decision_data['hand_rank'], decision_data['action_history'], decision_data['was_pfa'],
            decision_data['user_action'], decision_data['user_size'],
            decision_data['optimal_action'], decision_data['optimal_size'],
            decision_data['is_correct'], decision_data.get('decision_time', 0),
            datetime.now()
        ))
        
        decision_id = cursor.lastrowid
        
        # Log mistake if incorrect
        if not decision_data['is_correct']:
            mistake_type = self._classify_mistake(decision_data)
            severity = self._assess_mistake_severity(decision_data)
            description = self._generate_mistake_description(decision_data)
            
            cursor.execute('''
            INSERT INTO mistakes (
                session_id, decision_id, mistake_type, street, position,
                severity, description, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id, decision_id, mistake_type, decision_data['street'],
                decision_data['position'], severity, description, datetime.now()
            ))
        
        conn.commit()
        conn.close()
        return decision_id
    
    def end_session(self, session_id, total_hands, total_decisions, correct_decisions):
        """End a training session and calculate final stats."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        accuracy = (correct_decisions / total_decisions * 100) if total_decisions > 0 else 0
        
        cursor.execute('''
        UPDATE sessions 
        SET end_time = ?, total_hands = ?, total_decisions = ?, 
            correct_decisions = ?, accuracy = ?
        WHERE session_id = ?
        ''', (datetime.now(), total_hands, total_decisions, correct_decisions, accuracy, session_id))
        
        conn.commit()
        conn.close()
    
    def _classify_mistake(self, decision_data):
        """Classify the type of mistake made."""
        user_action = decision_data['user_action']
        optimal_action = decision_data['optimal_action']
        
        if user_action == 'fold' and optimal_action in ['call', 'raise']:
            return 'overfold'
        elif user_action in ['call', 'raise'] and optimal_action == 'fold':
            return 'overcall'
        elif user_action == 'call' and optimal_action == 'raise':
            return 'underaggression'
        elif user_action == 'raise' and optimal_action == 'call':
            return 'overaggression'
        elif user_action == 'check' and optimal_action == 'bet':
            return 'missed_value'
        elif user_action == 'bet' and optimal_action == 'check':
            return 'overbet'
        else:
            return 'other'
    
    def _assess_mistake_severity(self, decision_data):
        """Assess how severe the mistake was (low/medium/high)."""
        pot_size = decision_data['pot_size']
        to_call = decision_data['to_call']
        user_size = decision_data.get('user_size', 0)
        optimal_size = decision_data.get('optimal_size', 0)
        
        # Calculate cost of mistake in BB
        if decision_data['user_action'] == 'fold' and decision_data['optimal_action'] != 'fold':
            cost = pot_size  # Missed pot
        elif decision_data['user_action'] != 'fold' and decision_data['optimal_action'] == 'fold':
            cost = to_call + user_size  # Money lost
        else:
            cost = abs(user_size - optimal_size)  # Sizing error
        
        if cost < 2:
            return 'low'
        elif cost < 5:
            return 'medium'
        else:
            return 'high'
    
    def _generate_mistake_description(self, decision_data):
        """Generate a human-readable description of the mistake."""
        street = decision_data['street']
        position = decision_data['position']
        hand_rank = decision_data.get('hand_rank', 'unknown')
        user_action = decision_data['user_action']
        optimal_action = decision_data['optimal_action']
        
        return f"{street.title()} at {position}: {hand_rank} - played {user_action}, should have {optimal_action}"

class SessionAnalyzer:
    def __init__(self, db_path='holdem_sessions.db'):
        self.db_path = db_path
    
    def get_recent_performance(self, days=7):
        """Get performance statistics for recent sessions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
        SELECT session_id, start_time, accuracy, total_decisions
        FROM sessions 
        WHERE start_time >= ? AND end_time IS NOT NULL
        ORDER BY start_time DESC
        ''', (cutoff_date,))
        
        sessions = cursor.fetchall()
        conn.close()
        
        if not sessions:
            return None
        
        accuracies = [s[2] for s in sessions]
        total_decisions = sum(s[3] for s in sessions)
        
        return {
            'sessions_count': len(sessions),
            'avg_accuracy': statistics.mean(accuracies),
            'accuracy_trend': self._calculate_trend(accuracies),
            'total_decisions': total_decisions,
            'best_session': max(accuracies),
            'worst_session': min(accuracies)
        }
    
    def analyze_mistake_patterns(self, days=30):
        """Analyze patterns in mistakes to identify weak areas."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
        SELECT m.mistake_type, m.street, m.position, m.severity, d.hand_rank
        FROM mistakes m
        JOIN decisions d ON m.decision_id = d.decision_id
        WHERE m.timestamp >= ?
        ''', (cutoff_date,))
        
        mistakes = cursor.fetchall()
        conn.close()
        
        if not mistakes:
            return {}
        
        analysis = {
            'by_type': Counter(m[0] for m in mistakes),
            'by_street': Counter(m[1] for m in mistakes),
            'by_position': Counter(m[2] for m in mistakes),
            'by_severity': Counter(m[3] for m in mistakes),
            'by_hand_rank': Counter(m[4] for m in mistakes),
            'total_mistakes': len(mistakes)
        }
        
        return analysis
    
    def get_position_performance(self, days=30):
        """Analyze performance by position."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
        SELECT position, COUNT(*) as total, SUM(is_correct) as correct
        FROM decisions
        WHERE timestamp >= ?
        GROUP BY position
        ''', (cutoff_date,))
        
        results = cursor.fetchall()
        conn.close()
        
        performance = {}
        for pos, total, correct in results:
            performance[pos] = {
                'accuracy': (correct / total * 100) if total > 0 else 0,
                'total_decisions': total,
                'correct_decisions': correct
            }
        
        return performance
    
    def get_street_performance(self, days=30):
        """Analyze performance by street."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
        SELECT street, COUNT(*) as total, SUM(is_correct) as correct
        FROM decisions
        WHERE timestamp >= ?
        GROUP BY street
        ''', (cutoff_date,))
        
        results = cursor.fetchall()
        conn.close()
        
        performance = {}
        for street, total, correct in results:
            performance[street] = {
                'accuracy': (correct / total * 100) if total > 0 else 0,
                'total_decisions': total,
                'correct_decisions': correct
            }
        
        return performance
    
    def suggest_improvements(self):
        """Generate strategy improvement suggestions based on data."""
        mistake_patterns = self.analyze_mistake_patterns()
        position_perf = self.get_position_performance()
        street_perf = self.get_street_performance()
        
        suggestions = []
        
        # Analyze mistake patterns
        if mistake_patterns:
            top_mistake = mistake_patterns['by_type'].most_common(1)[0]
            suggestions.append(f"Focus on reducing '{top_mistake[0]}' mistakes - you have {top_mistake[1]} instances")
            
            worst_street = min(street_perf.items(), key=lambda x: x[1]['accuracy'])
            suggestions.append(f"Practice {worst_street[0]} decisions - current accuracy: {worst_street[1]['accuracy']:.1f}%")
            
            worst_position = min(position_perf.items(), key=lambda x: x[1]['accuracy'])
            suggestions.append(f"Study {worst_position[0]} play - weakest position at {worst_position[1]['accuracy']:.1f}%")
        
        return suggestions
    
    def _calculate_trend(self, values):
        """Calculate if performance is trending up or down."""
        if len(values) < 3:
            return 'insufficient_data'
        
        recent_avg = statistics.mean(values[:len(values)//2])
        older_avg = statistics.mean(values[len(values)//2:])
        
        if recent_avg > older_avg + 2:
            return 'improving'
        elif recent_avg < older_avg - 2:
            return 'declining'
        else:
            return 'stable'
    
    def print_comprehensive_report(self):
        """Print a comprehensive performance report."""
        print("\n" + "="*60)
        print("COMPREHENSIVE PERFORMANCE ANALYSIS")
        print("="*60)
        
        # Recent performance
        recent = self.get_recent_performance(7)
        if recent:
            print(f"\n📊 LAST 7 DAYS SUMMARY:")
            print(f"   Sessions: {recent['sessions_count']}")
            print(f"   Average Accuracy: {recent['avg_accuracy']:.1f}%")
            print(f"   Trend: {recent['accuracy_trend'].upper()}")
            print(f"   Total Decisions: {recent['total_decisions']}")
            print(f"   Best Session: {recent['best_session']:.1f}%")
            print(f"   Worst Session: {recent['worst_session']:.1f}%")
        
        # Mistake analysis
        mistakes = self.analyze_mistake_patterns(30)
        if mistakes:
            print(f"\n🎯 MISTAKE ANALYSIS (Last 30 Days):")
            print(f"   Total Mistakes: {mistakes['total_mistakes']}")
            print(f"   Most Common Type: {mistakes['by_type'].most_common(1)[0]}")
            print(f"   Worst Street: {mistakes['by_street'].most_common(1)[0]}")
            print(f"   Problem Position: {mistakes['by_position'].most_common(1)[0]}")
        
        # Performance by position
        pos_perf = self.get_position_performance(30)
        if pos_perf:
            print(f"\n📍 POSITION PERFORMANCE:")
            for pos, stats in sorted(pos_perf.items(), key=lambda x: x[1]['accuracy'], reverse=True):
                print(f"   {pos}: {stats['accuracy']:.1f}% ({stats['correct_decisions']}/{stats['total_decisions']})")
        
        # Performance by street
        street_perf = self.get_street_performance(30)
        if street_perf:
            print(f"\n🃏 STREET PERFORMANCE:")
            for street, stats in sorted(street_perf.items(), key=lambda x: x[1]['accuracy'], reverse=True):
                print(f"   {street.title()}: {stats['accuracy']:.1f}% ({stats['correct_decisions']}/{stats['total_decisions']})")
        
        # Improvement suggestions
        suggestions = self.suggest_improvements()
        if suggestions:
            print(f"\n💡 IMPROVEMENT SUGGESTIONS:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"   {i}. {suggestion}")
        
        print("\n" + "="*60)

def main():
    """Command-line interface for session analysis."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python session_logger.py report - Show comprehensive report")
        print("  python session_logger.py recent [days] - Show recent performance")
        print("  python session_logger.py mistakes [days] - Show mistake analysis")
        return
    
    analyzer = SessionAnalyzer()
    command = sys.argv[1]
    
    if command == 'report':
        analyzer.print_comprehensive_report()
    elif command == 'recent':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        recent = analyzer.get_recent_performance(days)
        if recent:
            print(json.dumps(recent, indent=2))
        else:
            print("No recent sessions found.")
    elif command == 'mistakes':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        mistakes = analyzer.analyze_mistake_patterns(days)
        if mistakes:
            print(json.dumps({k: dict(v) if hasattr(v, 'items') else v 
                            for k, v in mistakes.items()}, indent=2))
        else:
            print("No mistakes found in the specified period.")

if __name__ == '__main__':
    main()