import { useState, useEffect } from 'react';
import { fetchTenantConfig } from '../services/api';

/**
 * Hook to fetch and cache tenant configuration.
 * 
 * @returns {Object} { config, loading, error }
 */
export function useTenantConfig() {
    const [config, setConfig] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Check sessionStorage cache first
        const cached = sessionStorage.getItem('tenantConfig');
        if (cached) {
            try {
                setConfig(JSON.parse(cached));
                setLoading(false);
                return;
            } catch (e) {
                sessionStorage.removeItem('tenantConfig');
            }
        }

        // Fetch from API
        const fetchConfig = async () => {
            try {
                const data = await fetchTenantConfig();

                // Cache for session
                sessionStorage.setItem('tenantConfig', JSON.stringify(data));
                setConfig(data);
            } catch (err) {
                console.error('Failed to fetch tenant config:', err);
                setError(err.message || 'Failed to load configuration');

                // Fallback to hardcoded defaults (backward compatibility)
                setConfig(getDefaultConfig());
            } finally {
                setLoading(false);
            }
        };

        fetchConfig();
    }, []);

    return { config, loading, error };
}

/**
 * Fallback configuration if API fails.
 * Matches current hardcoded values for backward compatibility.
 */
function getDefaultConfig() {
    return {
        tenant_id: 'boss',
        display_name: 'Boss Security Screens',
        choices: {
            mesh: [
                ['10x10', '10x10 Standard'],
                ['12x12', '12x12 Standard'],
                ['12x12_american', '12x12 American'],
            ],
            frame_color: [
                ['Black', 'Black'],
                ['Dark Bronze', 'Dark Bronze'],
                ['Stucco', 'Stucco'],
                ['White', 'White'],
                ['Almond', 'Almond'],
            ],
            mesh_color: [
                ['Black', 'Black (Recommended)'],
                ['Stucco', 'Stucco'],
                ['Bronze', 'Bronze'],
            ],
            opacity: [
                ['80', '80%'],
                ['95', '95%'],
                ['99', '99%'],
            ],
        },
    };
}

export default useTenantConfig;
