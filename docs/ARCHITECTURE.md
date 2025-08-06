# 🏗️ **Technical Architecture Documentation**

## **Overview**

The Poker Strategy Practice System is designed as a modular, extensible application that allows users to develop, test, and refine their poker strategies through systematic practice and analysis.

## **🎯 System Goals**

### **Primary Objectives**
1. **Strategy Development**: Enable users to create and test custom poker strategies
2. **Dual Strategy Practice**: Practice against both user strategies and GTO strategies
3. **Real-time Analysis**: Provide immediate feedback on strategic decisions
4. **Comprehensive Logging**: Track all actions for post-session analysis
5. **Performance Tracking**: Measure strategy effectiveness over time

### **Technical Requirements**
- **Modularity**: Clean separation of concerns
- **Extensibility**: Easy to add new features and strategies
- **Performance**: Real-time analysis without affecting game performance
- **Reliability**: Robust error handling and data integrity
- **Usability**: Intuitive interface for strategy development

## **🏛️ Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
├─────────────────────────────────────────────────────────────┤
│  Practice Session UI  │  Strategy Analysis  │  Settings   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Application Logic Layer                   │
├─────────────────────────────────────────────────────────────┤
│  State Machine  │  Strategy Engine  │  Analysis Engine   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Data Management Layer                   │
├─────────────────────────────────────────────────────────────┤
│  Strategy Files  │  Session Data  │  Performance Metrics │
└─────────────────────────────────────────────────────────────┘
```

## **📁 Module Architecture**

### **1. Core Module (`backend/core/`)**

#### **`poker_state_machine.py`**
- **Purpose**: Central game logic and state management
- **Responsibilities**:
  - Game state transitions
  - Action validation and execution
  - Player management
  - Hand evaluation and winner determination
  - Session tracking and logging

#### **`hand_evaluation.py`**
- **Purpose**: Poker hand strength evaluation
- **Responsibilities**:
  - Hand classification (pairs, straights, flushes, etc.)
  - Hand strength calculation
  - Hand comparison for winner determination
  - Equity calculations

#### **`position_mapping.py`**
- **Purpose**: Position-based strategy mapping
- **Responsibilities**:
  - Table position management
  - Strategy position mapping
  - Position-aware decision making

#### **`gui_models.py`**
- **Purpose**: Data models for UI components
- **Responsibilities**:
  - Strategy data structures
  - Session data models
  - Analysis result models

### **2. UI Module (`backend/ui/`)**

#### **`practice_session_ui.py`**
- **Purpose**: Main practice session interface
- **Responsibilities**:
  - Game display and interaction
  - Action button management
  - Real-time feedback display
  - Session control

#### **`practice_session_ui_api.py`**
- **Purpose**: API layer for UI communication
- **Responsibilities**:
  - UI state management
  - Action routing
  - Data formatting for display

#### **`components/`**
- **Purpose**: Reusable UI components
- **Components**:
  - `tier_panel.py`: Strategy tier management
  - `decision_table_panel.py`: Decision analysis display
  - `hand_grid.py`: Hand selection interface
  - `tooltips.py`: Help and guidance system
  - `postflop_hs_editor.py`: Postflop strategy editor
  - `dialogs.py`: Modal dialogs and forms
  - `dynamic_position_manager.py`: Dynamic layout management

### **3. Strategy Module (`backend/strategy/`)**

#### **`strategy_engine.py`** (Future)
- **Purpose**: Core strategy decision engine
- **Responsibilities**:
  - Strategy loading and validation
  - Decision tree traversal
  - Action selection based on strategy
  - Strategy comparison and analysis

#### **`dual_strategy_manager.py`** (Future)
- **Purpose**: Manage user vs GTO strategies
- **Responsibilities**:
  - Strategy switching
  - Strategy comparison
  - Performance tracking

#### **`strategy_analyzer.py`** (Future)
- **Purpose**: Strategy analysis and optimization
- **Responsibilities**:
  - Deviation detection
  - Performance analysis
  - Improvement recommendations

### **4. Analysis Module (`backend/analysis/`)**

#### **`strategy_logger.py`** (Future)
- **Purpose**: Comprehensive action logging
- **Responsibilities**:
  - Decision point logging
  - Strategy compliance tracking
  - Performance metrics collection

#### **`performance_metrics.py`** (Future)
- **Purpose**: Performance analysis and reporting
- **Responsibilities**:
  - Win rate calculation
  - Decision accuracy measurement
  - Strategic effectiveness analysis

### **5. Data Module (`backend/data/`)**

#### **`strategies/`**
- **Purpose**: Strategy file storage and management
- **Structure**:
  - `user_strategies/`: User-created strategies
  - `gto_strategies/`: GTO strategy files
  - `templates/`: Strategy templates

#### **`modern_strategy.json`**
- **Purpose**: Default strategy configuration
- **Content**: Position-based decision trees and hand ranges

### **6. Utils Module (`backend/utils/`)**

#### **`pdf_export.py`**
- **Purpose**: Report generation and export
- **Responsibilities**:
  - Session report generation
  - Strategy analysis export
  - Performance metrics reporting

#### **`sound_config.json`**
- **Purpose**: Audio configuration
- **Content**: Sound mappings and voice settings

## **🔄 Data Flow**

### **Game Flow**
```
1. User Action → UI Layer
2. UI Layer → State Machine
3. State Machine → Strategy Engine
4. Strategy Engine → Decision
5. Decision → State Machine
6. State Machine → UI Update
7. UI Update → User Feedback
```

### **Analysis Flow**
```
1. Action Execution → Logger
2. Logger → Analysis Engine
3. Analysis Engine → Performance Metrics
4. Performance Metrics → Report Generation
5. Report Generation → User Display
```

## **🎯 Strategy System Design**

### **Strategy File Format**
```json
{
  "strategy_name": "Custom Strategy",
  "strategy_type": "user",
  "version": "1.0",
  "preflop": {
    "open_rules": {
      "UTG": {"threshold": 60, "sizing": 3.0},
      "MP": {"threshold": 55, "sizing": 3.0}
    },
    "vs_raise": {
      "UTG": {"value_thresh": 75, "call_thresh": 65, "sizing": 3.0}
    },
    "ranges": {
      "UTG": ["AA", "KK", "QQ", "AKs", "AKo"],
      "MP": ["AA", "KK", "QQ", "JJ", "AKs", "AKo", "AQs"]
    }
  },
  "postflop": {
    "flop": {
      "pfa": {
        "UTG": {"val_thresh": 30, "check_thresh": 15, "sizing": 0.75}
      },
      "caller": {
        "UTG": {"val_thresh": 25, "check_thresh": 10, "sizing": 0.5}
      }
    }
  }
}
```

### **Decision Engine Architecture**
```
Strategy File → Strategy Parser → Decision Tree → Action Selection
     ↓              ↓                ↓              ↓
Validation → Position Mapping → Context Analysis → Execution
```

## **🔧 State Management**

### **Game States**
- `START_HAND`: Hand initialization
- `PREFLOP_BETTING`: Preflop betting round
- `DEAL_FLOP`: Dealing community cards
- `FLOP_BETTING`: Flop betting round
- `DEAL_TURN`: Dealing turn card
- `TURN_BETTING`: Turn betting round
- `DEAL_RIVER`: Dealing river card
- `RIVER_BETTING`: River betting round
- `SHOWDOWN`: Hand evaluation
- `END_HAND`: Hand completion

### **State Transitions**
```
START_HAND → PREFLOP_BETTING → DEAL_FLOP → FLOP_BETTING
     ↓              ↓              ↓              ↓
END_HAND ← SHOWDOWN ← RIVER_BETTING ← DEAL_RIVER ← TURN_BETTING
```

## **📊 Performance Considerations**

### **Real-time Requirements**
- **UI Responsiveness**: < 100ms for user interactions
- **Analysis Latency**: < 50ms for real-time feedback
- **Strategy Loading**: < 200ms for strategy file loading

### **Memory Management**
- **Session Data**: Automatic cleanup after export
- **Strategy Cache**: LRU cache for frequently used strategies
- **UI Components**: Lazy loading for complex components

### **Scalability**
- **Modular Design**: Easy to add new features
- **Plugin Architecture**: Extensible strategy engines
- **Data Separation**: Clean separation of concerns

## **🛡️ Error Handling**

### **Strategy Validation**
- **File Format**: JSON schema validation
- **Completeness**: Required fields validation
- **Consistency**: Cross-reference validation

### **Game State Integrity**
- **State Transitions**: Valid transition checking
- **Action Validation**: Pre-execution validation
- **Data Consistency**: Post-execution verification

### **User Experience**
- **Graceful Degradation**: Fallback to basic functionality
- **Error Recovery**: Automatic state recovery
- **User Feedback**: Clear error messages

## **🔮 Future Enhancements**

### **Planned Features**
1. **Advanced Strategy Engine**: Complex decision trees
2. **Machine Learning Integration**: Adaptive strategy optimization
3. **Multi-table Support**: Simultaneous practice sessions
4. **Cloud Synchronization**: Strategy sharing and backup
5. **Tournament Mode**: Multi-player practice sessions

### **Technical Improvements**
1. **Performance Optimization**: Caching and lazy loading
2. **Memory Management**: Better resource utilization
3. **Error Handling**: More robust error recovery
4. **Testing Coverage**: Comprehensive test suite
5. **Documentation**: API and user documentation

---

**🎯 Architecture Goal**: Create a robust, extensible platform for poker strategy development and practice that provides comprehensive analysis and feedback while maintaining excellent performance and user experience. 