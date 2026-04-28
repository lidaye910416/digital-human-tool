import React, { useState, useEffect, useRef } from 'react';
import { View, Text, Animated, PanResponder, StyleSheet, TouchableOpacity } from '@tarojs/components';
import { ANIMATION, EASING } from '../../../../shared/constants';

interface DatePickerProps {
  visible: boolean;
  currentDate: string; // YYYY-MM-DD
  onDateChange: (date: string) => void;
  onClose: () => void;
}

interface DateItem {
  label: string;
  value: string; // YYYY-MM-DD
  isToday: boolean;
}

const DatePicker: React.FC<DatePickerProps> = ({
  visible,
  currentDate,
  onDateChange,
  onClose
}) => {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [dates, setDates] = useState<DateItem[]>([]);
  const translateY = useRef(new Animated.Value(visible ? 0 : -300)).current;
  const backdropOpacity = useRef(new Animated.Value(visible ? 0 : 0)).current;
  const scrollY = useRef(new Animated.Value(0)).current;

  // Generate dates (today, yesterday, and last 6 days)
  useEffect(() => {
    const generateDates = () => {
      const items: DateItem[] = [];
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      for (let i = 0; i < 30; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const value = date.toISOString().split('T')[0];
        const isToday = i === 0;
        
        let label: string;
        if (isToday) {
          label = '今天';
        } else if (i === 1) {
          label = '昨天';
        } else {
          label = `${date.getMonth() + 1}月${date.getDate()}日`;
        }

        items.push({ label, value, isToday });
      }
      return items;
    };

    setDates(generateDates());
    
    // Find index of current date
    const idx = dates.findIndex(d => d.value === currentDate);
    if (idx >= 0) setSelectedIndex(idx);
  }, [currentDate]);

  // Animation when visible changes
  useEffect(() => {
    Animated.parallel([
      Animated.timing(translateY, {
        toValue: visible ? 0 : -300,
        duration: ANIMATION.SLOW,
        easing: EASING.OUT as any,
        useNativeDriver: true,
      }),
      Animated.timing(backdropOpacity, {
        toValue: visible ? 1 : 0,
        duration: ANIMATION.SLOW,
        useNativeDriver: true,
      })
    ]).start();
  }, [visible]);

  const handleSelect = (index: number) => {
    setSelectedIndex(index);
    const date = dates[index];
    if (date) {
      onDateChange(date.value);
    }
    // Animate out
    Animated.parallel([
      Animated.timing(translateY, {
        toValue: -300,
        duration: ANIMATION.NORMAL,
        easing: EASING.OUT as any,
        useNativeDriver: true,
      }),
      Animated.timing(backdropOpacity, {
        toValue: 0,
        duration: ANIMATION.NORMAL,
        useNativeDriver: true,
      })
    ]).start(() => onClose());
  };

  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onMoveShouldSetPanResponder: () => true,
      onPanResponderMove: (_, gestureState) => {
        // Simulate wheel scrolling with inertia
        const newY = gestureState.dy;
        scrollY.setValue(newY);
      },
      onPanResponderRelease: (_, gestureState) => {
        const velocity = gestureState.vy;
        const distance = gestureState.dy;
        
        // Determine direction and how many items to scroll
        let newIndex = selectedIndex;
        if (velocity < -0.5 || distance < -50) {
          newIndex = Math.max(0, selectedIndex - 1);
        } else if (velocity > 0.5 || distance > 50) {
          newIndex = Math.min(dates.length - 1, selectedIndex + 1);
        }

        // Animate to new position
        setSelectedIndex(newIndex);
        onDateChange(dates[newIndex]?.value || currentDate);
      }
    })
  ).current;

  if (!visible) return null;

  const selectedDate = dates[selectedIndex];

  return (
    <View style={styles.container}>
      {/* Backdrop */}
      <Animated.View 
        style={[
          styles.backdrop,
          { opacity: backdropOpacity }
        ]}
        onClick={onClose}
      />
      
      {/* Picker Panel */}
      <Animated.View 
        style={[
          styles.panel,
          { transform: [{ translateY }] }
        ]}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>选择日期</Text>
          <TouchableOpacity onClick={onClose} style={styles.closeBtn}>
            <Text style={styles.closeText}>取消</Text>
          </TouchableOpacity>
        </View>

        {/* Quick Buttons */}
        <View style={styles.quickBtns}>
          <TouchableOpacity 
            style={[styles.quickBtn, selectedDate?.isToday && styles.quickBtnActive]}
            onClick={() => handleSelect(0)}
          >
            <Text style={[styles.quickBtnText, selectedDate?.isToday && styles.quickBtnTextActive]}>今天</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.quickBtn, dates[1]?.value === selectedDate?.value && !selectedDate?.isToday && styles.quickBtnActive]}
            onClick={() => handleSelect(1)}
          >
            <Text style={[styles.quickBtnText, dates[1]?.value === selectedDate?.value && !selectedDate?.isToday && styles.quickBtnTextActive]}>昨天</Text>
          </TouchableOpacity>
        </View>

        {/* Wheel Selector */}
        <View style={styles.wheelContainer} {...panResponder.panHandlers}>
          <View style={styles.indicator} />
          {dates.slice(Math.max(0, selectedIndex - 2), selectedIndex + 3).map((date, idx) => {
            const itemIndex = Math.max(0, selectedIndex - 2) + idx;
            const isSelected = itemIndex === selectedIndex;
            const distance = Math.abs(itemIndex - selectedIndex);
            const scale = isSelected ? 1.2 : 1 - distance * 0.1;
            const opacity = isSelected ? 1 : 0.4;
            
            return (
              <Animated.View
                key={date.value}
                style={[
                  styles.wheelItem,
                  isSelected && styles.wheelItemSelected,
                  {
                    opacity,
                    transform: [{ scale }],
                  }
                ]}
              >
                <Text style={[styles.wheelItemText, isSelected && styles.wheelItemTextSelected]}>
                  {date.label}
                </Text>
              </Animated.View>
            );
          })}
        </View>

        {/* Confirm Button */}
        <TouchableOpacity style={styles.confirmBtn} onClick={() => handleSelect(selectedIndex)}>
          <Text style={styles.confirmBtnText}>确定</Text>
        </TouchableOpacity>
      </Animated.View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 1000,
  },
  backdrop: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    backdropFilter: 'blur(8px)',
  },
  panel: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    backgroundColor: '#18181b',
    borderRadius: '0 0 24px 24px',
    paddingTop: 48,
    paddingBottom: 32,
    paddingHorizontal: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fafafa',
  },
  closeBtn: {
    padding: 8,
  },
  closeText: {
    fontSize: 14,
    color: '#71717a',
  },
  quickBtns: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  quickBtn: {
    paddingVertical: 8,
    paddingHorizontal: 20,
    backgroundColor: '#27272a',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#3f3f46',
  },
  quickBtnActive: {
    backgroundColor: '#6366f1',
    borderColor: '#6366f1',
  },
  quickBtnText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#a1a1aa',
  },
  quickBtnTextActive: {
    color: '#ffffff',
  },
  wheelContainer: {
    height: 180,
    position: 'relative',
    justifyContent: 'center',
    alignItems: 'center',
  },
  indicator: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: '50%',
    marginTop: -25,
    height: 50,
    backgroundColor: 'rgba(99, 102, 241, 0.15)',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#6366f1',
  },
  wheelItem: {
    position: 'absolute',
    paddingVertical: 12,
    paddingHorizontal: 24,
  },
  wheelItemSelected: {
    zIndex: 10,
  },
  wheelItemText: {
    fontSize: 16,
    color: '#71717a',
    textAlign: 'center',
  },
  wheelItemTextSelected: {
    color: '#fafafa',
    fontWeight: '600',
  },
  confirmBtn: {
    marginTop: 24,
    backgroundColor: '#6366f1',
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
  },
  confirmBtnText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
});

export default DatePicker;
