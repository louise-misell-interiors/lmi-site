import babel from 'rollup-plugin-babel';
import cjs from 'rollup-plugin-commonjs';
import globals from 'rollup-plugin-node-globals';
import replace from 'rollup-plugin-replace';
import resolve from 'rollup-plugin-node-resolve';
import { uglify } from 'rollup-plugin-uglify';

export default {
    input: 'lmisite/bookings/static/bookings/js/main.js',
    output: {
        file: 'lmisite/bookings/static/bookings/js/main_production.js',
        name: 'main',
        sourcemap: true,
        format: 'iife',
    },
    context: 'window',
    plugins: [
        resolve({
            jsnext: true,
            browser: true,
        }),
        babel({
            babelrc: false,
            exclude: 'node_modules/**',
            presets: [['env', {modules: false}], 'stage-0', 'react'],
            plugins: ['external-helpers']
        }),
        cjs({
            include: [
                'node_modules/**',
            ],
            exclude: [
                'node_modules/process-es6/**'
            ],
            namedExports: {
                'node_modules/react/index.js': ['Children', 'Component', 'PropTypes', 'createElement'],
                'node_modules/react-dom/index.js': ['render'],
                'node_modules/graphql-anywhere/lib/async.js': ['graphql'],
            }
        }),
        globals(),
        replace({'process.env.NODE_ENV': JSON.stringify('development')}),
        uglify()
    ]
};