import React, { useRef, useEffect, useState } from 'react';
import { View, Text, ScrollView, Animated, TouchableOpacity, StyleSheet } from '@tarojs/components';
import { CATEGORIES, ANIMATION, EASING } from '../../../../shared/constants';

interface CategoryTabsProps {
  activeCategory: string;
  onCategoryChange: (category: string) => void;
}

const CategoryTabs: React.FC<CategoryTabsProps> = ({
  activeCategory,
  onCategoryChange
}) => {
  const scrollRef = useRef<any>(null);
  const indicatorWidth = useRef(new Animated.Value(0)).current;
  const indicatorLeft = useRef(new Animated.Value(0)).current;
  const contentOpacity = useRef(new Animated.Value(1)).current;
  const [tabPositions, setTabPositions] = useState<{ [key: string]: { left: number; width: number } }>({});

  // Update indicator position when active category changes
  useEffect(() => {
    const position = tabPositions[activeCategory];
    if (position) {
      Animated.parallel([
        Animated.spring(indicatorLeft, {
          toValue: position.left,
          friction: 8,
          tension: 100,
          useNativeDriver: false,
        }),
        Animated.spring(indicatorWidth, {
          toValue: position.width,
          friction: 8,
          tension: 100,
          useNativeDriver: false,
        })
      ]).start();

      // Scroll into view
      scrollRef.current?.scrollTo({
        x: Math.max(0, position.left - 50),
        animated: true,
      });
    }
  }, [activeCategory, tabPositions]);

  const handleTabPress = (categoryId: string) => {
    if (categoryId === activeCategory) return;

    // Fade out content
    Animated.timing(contentOpacity, {
      toValue: 0.3,
      duration: ANIMATION.FAST,
      useNativeDriver: true,
    }).start(() => {
      onCategoryChange(categoryId);
      // Fade in content
      Animated.timing(contentOpacity, {
        toValue: 1,
        duration: ANIMATION.NORMAL,
        useNativeDriver: true,
      }).start();
    });
  };

  const handleLayout = (categoryId: string, event: any) => {
    const { x, width } = event.nativeEvent.layout;
    setTabPositions(prev => ({
      ...prev,
      [categoryId]: { left: x, width }
    }));
  };

  return (
    <View style={styles.container}>
      <ScrollView
        ref={scrollRef}
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
      >
        {CATEGORIES.map((category) => {
          const isActive = activeCategory === category.id;
          return (
            <TouchableOpacity
              key={category.id}
              onPress={() => handleTabPress(category.id)}
              onLayout={(e) => handleLayout(category.id, e)}
              style={styles.tab}
              activeOpacity={0.7}
            >
              <View style={styles.tabContent}>
                <Text style={styles.tabEmoji}>{category.emoji}</Text>
                <Text style={[styles.tabText, isActive && styles.tabTextActive]}>
                  {category.name}
                </Text>
              </View>
            </TouchableOpacity>
          );
        })}
        
        {/* Sliding Indicator */}
        <Animated.View
          style={[
            styles.indicator,
            {
              width: indicatorWidth,
              left: indicatorLeft,
            }
          ]}
        />
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#09090b',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.08)',
  },
  scrollView: {
    flexGrow: 0,
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 8,
  },
  tab: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 20,
    backgroundColor: '#18181b',
    marginRight: 8,
    position: 'relative',
  },
  tabContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  tabEmoji: {
    fontSize: 14,
  },
  tabText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#71717a',
  },
  tabTextActive: {
    color: '#fafafa',
    fontWeight: '600',
  },
  indicator: {
    position: 'absolute',
    bottom: 0,
    height: 2,
    backgroundColor: '#6366f1',
    borderRadius: 1,
  },
});

export default CategoryTabs;
