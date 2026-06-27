import React, {useState} from 'react';
import {
  Dimensions,
  SafeAreaView,
  StatusBar,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

const {width} = Dimensions.get('window');
const BTN_GAP = 13;
const BTN_SIZE = (width - 40 - BTN_GAP * 3) / 4;

type ButtonValue =
  | '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9'
  | '.' | '+' | '-' | '×' | '÷' | '=' | 'AC' | '+/-' | '%';

interface CalcState {
  display: string;
  expression: string;
  history: string;
  previousValue: number | null;
  operator: string | null;
  waitingForOperand: boolean;
}

const INITIAL_STATE: CalcState = {
  display: '0',
  expression: '',
  history: '',
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

function formatNumber(value: string): string {
  const num = parseFloat(value);
  if (isNaN(num)) return 'エラー';
  if (value.endsWith('.')) return value;
  if (Math.abs(num) >= 1e10) return num.toExponential(3);
  const parts = value.split('.');
  parts[0] = Number(parts[0]).toLocaleString('ja-JP');
  return parts.join('.');
}

export default function App(): React.JSX.Element {
  const [state, setState] = useState<CalcState>(INITIAL_STATE);

  const handleNumber = (num: string) => {
    setState(prev => {
      if (prev.waitingForOperand) {
        return {
          ...prev,
          display: num,
          expression: prev.expression + num,
          waitingForOperand: false,
        };
      }
      const newDisplay =
        prev.display === '0' && num !== '.'
          ? num
          : prev.display.includes('.') && num === '.'
          ? prev.display
          : prev.display + num;
      return {
        ...prev,
        display: newDisplay,
        expression: prev.expression.slice(0, -prev.display.length) + newDisplay,
      };
    });
  };

  const handleOperator = (op: string) => {
    setState(prev => {
      const current = parseFloat(prev.display);
      if (prev.previousValue !== null && !prev.waitingForOperand) {
        const result = calculate(prev.previousValue, current, prev.operator!);
        const resultStr = String(result);
        return {
          display: resultStr,
          expression: formatNumber(resultStr) + ' ' + op + ' ',
          history: prev.expression,
          previousValue: result,
          operator: op,
          waitingForOperand: true,
        };
      }
      return {
        ...prev,
        expression: formatNumber(prev.display) + ' ' + op + ' ',
        history: prev.history,
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
      const resultStr = String(result);
      return {
        display: resultStr,
        expression: '',
        history: prev.expression + formatNumber(prev.display) + ' =',
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

  const isOperator = (v: string) => ['+', '-', '×', '÷'].includes(v);
  const isActiveOp = (v: string) => state.operator === v && state.waitingForOperand;

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" backgroundColor="#050510" />
      <View style={styles.container}>
        {/* Display */}
        <View style={styles.displayContainer}>
          <Text style={styles.historyText} numberOfLines={1}>
            {state.history}
          </Text>
          <Text style={styles.expressionText} numberOfLines={1}>
            {state.expression}
          </Text>
          <Text
            style={styles.resultText}
            numberOfLines={1}
            adjustsFontSizeToFit
            minimumFontScale={0.4}>
            {formatNumber(state.display)}
          </Text>
        </View>

        {/* Buttons */}
        <View style={styles.buttonsContainer}>
          {buttons.map((row, rowIndex) => (
            <View key={rowIndex} style={styles.row}>
              {row.map(value => {
                const isZero = value === '0';
                const isOp = isOperator(value);
                const isEq = value === '=';
                const isFunc = ['AC', '+/-', '%'].includes(value);
                const active = isActiveOp(value);

                return (
                  <TouchableOpacity
                    key={value}
                    style={[
                      styles.btn,
                      isZero && styles.btnWide,
                      isFunc && styles.btnFunc,
                      isOp && styles.btnOp,
                      isEq && styles.btnEq,
                      active && styles.btnOpActive,
                    ]}
                    onPress={() => handlePress(value)}
                    activeOpacity={0.65}>
                    <Text
                      style={[
                        styles.btnText,
                        isFunc && styles.btnTextFunc,
                        isOp && styles.btnTextOp,
                        isEq && styles.btnTextOp,
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

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#050510',
  },
  container: {
    flex: 1,
    backgroundColor: '#050510',
    justifyContent: 'flex-end',
    paddingHorizontal: 20,
    paddingBottom: 28,
  },
  displayContainer: {
    alignItems: 'flex-end',
    paddingHorizontal: 6,
    paddingBottom: 24,
    gap: 4,
  },
  historyText: {
    color: 'rgba(255,255,255,0.2)',
    fontSize: 16,
    fontWeight: '300',
    letterSpacing: 0.5,
    minHeight: 22,
  },
  expressionText: {
    color: 'rgba(255,255,255,0.4)',
    fontSize: 22,
    fontWeight: '300',
    letterSpacing: 1,
    minHeight: 30,
  },
  resultText: {
    color: '#fff',
    fontSize: 80,
    fontWeight: '200',
    letterSpacing: -3,
    lineHeight: 88,
  },
  buttonsContainer: {
    gap: BTN_GAP,
  },
  row: {
    flexDirection: 'row',
    gap: BTN_GAP,
  },
  btn: {
    width: BTN_SIZE,
    height: BTN_SIZE,
    borderRadius: 22,
    backgroundColor: '#1a1a28',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.06)',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.5,
    shadowRadius: 8,
    elevation: 8,
  },
  btnWide: {
    width: BTN_SIZE * 2 + BTN_GAP,
    alignItems: 'flex-start',
    paddingLeft: 24,
  },
  btnFunc: {
    backgroundColor: '#1e1e30',
    borderColor: 'rgba(255,255,255,0.08)',
  },
  btnOp: {
    backgroundColor: '#6B2FE0',
    borderWidth: 0,
    shadowColor: '#7B3FF5',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.6,
    shadowRadius: 12,
    elevation: 12,
  },
  btnOpActive: {
    backgroundColor: '#8B4FFF',
    shadowOpacity: 0.8,
    shadowRadius: 18,
  },
  btnEq: {
    backgroundColor: '#E8420A',
    borderWidth: 0,
    shadowColor: '#FF6B35',
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 0.6,
    shadowRadius: 12,
    elevation: 12,
  },
  btnText: {
    color: '#d0d0e8',
    fontSize: 28,
    fontWeight: '400',
  },
  btnTextFunc: {
    color: '#9090b8',
    fontSize: 18,
    fontWeight: '500',
    letterSpacing: 0.5,
  },
  btnTextOp: {
    color: '#fff',
    fontSize: 26,
    fontWeight: '400',
  },
});
