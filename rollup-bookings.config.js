import babel from '@rollup/plugin-babel';
import cjs from '@rollup/plugin-commonjs';
import globals from 'rollup-plugin-node-globals';
import replace from '@rollup/plugin-replace';
import resolve from '@rollup/plugin-node-resolve';
import postcss from 'rollup-plugin-postcss';
import svg from 'rollup-plugin-svg';
import { terser } from "rollup-plugin-terser";

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
        postcss({
            plugins: []
        }),
        svg(),
        resolve({
            jsnext: true,
            browser: true,
        }),
        babel({
            babelrc: false,
            exclude: 'node_modules/**',
            presets: [['@babel/env', {modules: false}], '@babel/react'],
//            plugins: ['@babel/external-helpers'],
            babelHelpers: 'bundled'
        }),
        cjs({
            include: [
                'node_modules/**',
            ],
            exclude: [
                'node_modules/process-es6/**'
            ],
        }),
        globals(),
        replace({'process.env.NODE_ENV': JSON.stringify('production')}),
        terser()
    ]
};
