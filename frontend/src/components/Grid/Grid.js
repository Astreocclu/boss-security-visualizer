import React from 'react';
import PropTypes from 'prop-types';
import './Grid.css';

const Container = ({ 
  children, 
  fluid = false, 
  className = '',
  ...props 
}) => {
  const containerClasses = [
    'container',
    fluid && 'container-fluid',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={containerClasses} {...props}>
      {children}
    </div>
  );
};

const Row = ({ 
  children, 
  gutter = 'medium',
  align = 'stretch',
  justify = 'start',
  className = '',
  ...props 
}) => {
  const rowClasses = [
    'row',
    `row-gutter-${gutter}`,
    `row-align-${align}`,
    `row-justify-${justify}`,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={rowClasses} {...props}>
      {children}
    </div>
  );
};

const Col = ({ 
  children,
  xs,
  sm,
  md,
  lg,
  xl,
  offset,
  className = '',
  ...props 
}) => {
  const colClasses = [
    'col',
    xs && `col-xs-${xs}`,
    sm && `col-sm-${sm}`,
    md && `col-md-${md}`,
    lg && `col-lg-${lg}`,
    xl && `col-xl-${xl}`,
    offset && `col-offset-${offset}`,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={colClasses} {...props}>
      {children}
    </div>
  );
};

Container.propTypes = {
  children: PropTypes.node.isRequired,
  fluid: PropTypes.bool,
  className: PropTypes.string
};

Row.propTypes = {
  children: PropTypes.node.isRequired,
  gutter: PropTypes.oneOf(['none', 'small', 'medium', 'large']),
  align: PropTypes.oneOf(['start', 'center', 'end', 'stretch']),
  justify: PropTypes.oneOf(['start', 'center', 'end', 'between', 'around', 'evenly']),
  className: PropTypes.string
};

Col.propTypes = {
  children: PropTypes.node.isRequired,
  xs: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  sm: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  md: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  lg: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  xl: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  offset: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  className: PropTypes.string
};

export { Container, Row, Col };
export default { Container, Row, Col };
