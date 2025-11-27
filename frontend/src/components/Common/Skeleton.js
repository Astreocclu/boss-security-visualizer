import React from 'react';
import PropTypes from 'prop-types';
import './Skeleton.css';

const Skeleton = ({
    variant = 'text',
    width,
    height,
    animation = 'pulse',
    className = '',
    style = {},
    ...props
}) => {
    const styles = {
        width,
        height,
        ...style,
    };

    return (
        <span
            className={`skeleton ${variant} ${animation} ${className}`}
            style={styles}
            {...props}
        />
    );
};

Skeleton.propTypes = {
    variant: PropTypes.oneOf(['text', 'rectangular', 'circular']),
    width: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    height: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    animation: PropTypes.oneOf(['pulse', 'wave', false]),
    className: PropTypes.string,
    style: PropTypes.object,
};

export default Skeleton;
