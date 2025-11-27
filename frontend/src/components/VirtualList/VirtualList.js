import React, { useState, useEffect, useRef, useMemo } from 'react';
import PropTypes from 'prop-types';
import './VirtualList.css';

const VirtualList = ({
  items = [],
  itemHeight = 50,
  containerHeight = 400,
  renderItem,
  overscan = 5,
  className = '',
  onScroll,
  ...props
}) => {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef(null);

  const visibleRange = useMemo(() => {
    const containerHeightValue = typeof containerHeight === 'string' 
      ? parseInt(containerHeight) 
      : containerHeight;
    
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      items.length - 1,
      Math.ceil((scrollTop + containerHeightValue) / itemHeight) + overscan
    );

    return { startIndex, endIndex };
  }, [scrollTop, itemHeight, containerHeight, items.length, overscan]);

  const totalHeight = items.length * itemHeight;
  const offsetY = visibleRange.startIndex * itemHeight;

  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.startIndex, visibleRange.endIndex + 1);
  }, [items, visibleRange.startIndex, visibleRange.endIndex]);

  const handleScroll = (e) => {
    const newScrollTop = e.target.scrollTop;
    setScrollTop(newScrollTop);
    onScroll?.(e, newScrollTop);
  };

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.scrollTop = scrollTop;
    }
  }, [scrollTop]);

  const containerClasses = [
    'virtual-list',
    className
  ].filter(Boolean).join(' ');

  return (
    <div
      ref={containerRef}
      className={containerClasses}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
      {...props}
    >
      <div
        className="virtual-list-spacer"
        style={{ height: totalHeight }}
      >
        <div
          className="virtual-list-content"
          style={{
            transform: `translateY(${offsetY}px)`,
            height: (visibleRange.endIndex - visibleRange.startIndex + 1) * itemHeight
          }}
        >
          {visibleItems.map((item, index) => {
            const actualIndex = visibleRange.startIndex + index;
            return (
              <div
                key={item.id || actualIndex}
                className="virtual-list-item"
                style={{ height: itemHeight }}
              >
                {renderItem(item, actualIndex)}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

VirtualList.propTypes = {
  items: PropTypes.array.isRequired,
  itemHeight: PropTypes.number,
  containerHeight: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  renderItem: PropTypes.func.isRequired,
  overscan: PropTypes.number,
  className: PropTypes.string,
  onScroll: PropTypes.func
};

// Hook for virtual scrolling with dynamic item heights
export const useVirtualList = ({
  items,
  estimatedItemHeight = 50,
  containerHeight = 400,
  overscan = 5
}) => {
  const [scrollTop, setScrollTop] = useState(0);
  const [itemHeights, setItemHeights] = useState(new Map());
  const containerRef = useRef(null);

  const getItemHeight = (index) => {
    return itemHeights.get(index) || estimatedItemHeight;
  };

  const getTotalHeight = () => {
    let height = 0;
    for (let i = 0; i < items.length; i++) {
      height += getItemHeight(i);
    }
    return height;
  };

  const getVisibleRange = () => {
    let startIndex = 0;
    let endIndex = 0;
    let accumulatedHeight = 0;

    // Find start index
    for (let i = 0; i < items.length; i++) {
      const itemHeight = getItemHeight(i);
      if (accumulatedHeight + itemHeight > scrollTop) {
        startIndex = Math.max(0, i - overscan);
        break;
      }
      accumulatedHeight += itemHeight;
    }

    // Find end index
    accumulatedHeight = 0;
    for (let i = 0; i < items.length; i++) {
      const itemHeight = getItemHeight(i);
      accumulatedHeight += itemHeight;
      if (accumulatedHeight > scrollTop + containerHeight) {
        endIndex = Math.min(items.length - 1, i + overscan);
        break;
      }
    }

    return { startIndex, endIndex };
  };

  const getOffsetForIndex = (index) => {
    let offset = 0;
    for (let i = 0; i < index; i++) {
      offset += getItemHeight(i);
    }
    return offset;
  };

  const setItemHeight = (index, height) => {
    setItemHeights(prev => new Map(prev).set(index, height));
  };

  return {
    containerRef,
    scrollTop,
    setScrollTop,
    getVisibleRange,
    getTotalHeight,
    getOffsetForIndex,
    setItemHeight
  };
};

export default React.memo(VirtualList);
