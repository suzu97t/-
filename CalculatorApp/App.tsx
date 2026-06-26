import React, {useState} from 'react';
import {
  SafeAreaView,
  StatusBar,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

type ButtonValue =
  | '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9'
  | '.' | '+' | '-' | '×' | '÷' | '=' | 'AC' | '+/-' | '%';

interface CalcState {
  display: string;
  previousValue: number | null;
  operator: string | null;
  waitingForOperand: boolean;
}

const INITIAL_STATE: CalcState = {
  display: '0',
  previousValue: null,
  operator: null,
  waitingForOperand: false,
};

function calculate(a: number, b: number, op: string): number {
  switch (op) {
    case '+': return a + b;
    case '-': return a - b;
    case '×': return a * b;
    case '÷': return b !== 0 ? a / b : NaN;
    default: return b;
  }
}

function formatDisplay(value: string): string {
  const num = parseFloat(value);
  if (isNaN(num)) return 'エラー';
  if (value.endsWith('.')) return value;
  if (Math.abs(num) >= 1e10 || (Math.abs(num) < 1e-6 && num !== 0)) {
    return num.toExponential(4);
  }
  const parts = value.split('.');
  parts[0] = Number(parts[0]).toLocaleString('ja-JP');
  return parts.join('.');
}

export default function App(): React.JSX.Element {
  const [state, setState] = useState<CalcState>(INITIAL_STATE);

  const handleNumber = (num: string) => {
    setState(prev => {
      if (prev.waitingForOperand) {
        return {...prev, display: num, waitingForOperand: false};
      }
      if (prev.display === '0' && num !== '.') {
        return {...prev, display: num};
      }
      if (num === '.' && prev.display.includes('.')) {
        return prev;
      }
      return {...prev, display: prev.display + num};
    });
  };

  const handleOperator = (op: string) => {
    setState(prev => {
      const current = parseFloat(prev.display);
      if (prev.previousValue !== null && !prev.waitingForOperand) {
        const result = calculate(prev.previousValue, current, prev.operator!);
        return {
          display: String(result),
          previousValue: result,
          operator: op,
          waitingForOperand: true,
        };
      }
      return {
        ...prev,
        previousValue: current,
        operator: op,
        waitingForOperand: true,
      };
    });
  };

  const handleEquals = () => {
    setState(prev => {
      if (prev.previousValue === null || prev.operator === null) return prev;
      const current = parseFloat(prev.display);
      const result = calculate(prev.previousValue, current, prev.operator);
      return {
        display: String(result),
        previousValue: null,
        operator: null,
        waitingForOperand: true,
      };
    });
  };

  const handleAC = () => setState(INITIAL_STATE);

  const handlePlusMinus = () => {
    setState(prev => ({
      ...prev,
      display: String(parseFloat(prev.display) * -1),
    }));
  };

  const handlePercent = () => {
    setState(prev => ({
      ...prev,
      display: String(parseFloat(prev.display) / 100),
    }));
  };

  const handlePress = (value: ButtonValue) => {
    if ('0123456789.'.includes(value)) {
      handleNumber(value);
    } else if (['+', '-', '×', '÷'].includes(value)) {
      handleOperator(value);
    } else if (value === '=') {
      handleEquals();
    } else if (value === 'AC') {
      handleAC();
    } else if (value === '+/-') {
      handlePlusMinus();
    } else if (value === '%') {
      handlePercent();
    }
  };

  const buttons: ButtonValue[][] = [
    ['AC', '+/-', '%', '÷'],
    ['7', '8', '9', '×'],
    ['4', '5', '6', '-'],
    ['1', '2', '3', '+'],
    ['0', '.', '='],
  ];

  const isOperator = (v: string) => ['+', '-', '×', '÷', '='].includes(v);
  const isFuncButton = (v: string) => ['AC', '+/-', '%'].includes(v);

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" backgroundColor="#000" />
      <View style={styles.container}>
        <View style={styles.displayContainer}>
          <Text style={styles.displayText} numberOfLines={1} adjustsFontSizeToFit>
            {formatDisplay(state.display)}
          </Text>
        </View>
        <View style={styles.buttonsContainer}>
          {buttons.map((row, rowIndex) => (
            <View key={rowIndex} style={styles.row}>
              {row.map(value => {
                const isZero = value === '0';
                const isOp = isOperator(value);
                const isActive = isOp && state.operator === value && state.waitingForOperand;
                const isFunc = isFuncButton(value);
                return (
                  <TouchableOpacity
                    key={value}
                    style={[
                      styles.button,
                      isZero && styles.buttonWide,
                      isOp && styles.buttonOperator,
                      isFunc && styles.buttonFunc,
                      isActive && styles.buttonOperatorActive,
                    ]}
                    onPress={() => handlePress(value)}
                    activeOpacity={0.7}>
                    <Text
                      style={[
                        styles.buttonText,
                        isOp && styles.buttonTextOperator,
                        isFunc && styles.buttonTextFunc,
                        isActive && styles.buttonTextActive,
                      ]}>
                      {value}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </View>
          ))}
        </View>
      </View>
    </SafeAreaView>
  );
}

const BTN_SIZE = 80;
const BTN_GAP = 12;

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#000',
  },
  container: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'flex-end',
    paddingHorizontal: 16,
    paddingBottom: 20,
  },
  displayContainer: {
    alignItems: 'flex-end',
    paddingHorizontal: 8,
    paddingBottom: 16,
    minHeight: 100,
    justifyContent: 'flex-end',
  },
  displayText: {
    color: '#fff',
    fontSize: 72,
    fontWeight: '200',
  },
  buttonsContainer: {
    gap: BTN_GAP,
  },
  row: {
    flexDirection: 'row',
    gap: BTN_GAP,
  },
  button: {
    width: BTN_SIZE,
    height: BTN_SIZE,
    borderRadius: BTN_SIZE / 2,
    backgroundColor: '#333',
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonWide: {
    width: BTN_SIZE * 2 + BTN_GAP,
    alignItems: 'flex-start',
    paddingLeft: 28,
  },
  buttonOperator: {
    backgroundColor: '#FF9F0A',
  },
  buttonOperatorActive: {
    backgroundColor: '#fff',
  },
  buttonFunc: {
    backgroundColor: '#A5A5A5',
  },
  buttonText: {
    color: '#fff',
    fontSize: 32,
    fontWeight: '400',
  },
  buttonTextOperator: {
    color: '#fff',
  },
  buttonTextActive: {
    color: '#FF9F0A',
  },
  buttonTextFunc: {
    color: '#000',
  },
});
