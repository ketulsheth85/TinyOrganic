const isTest = process.env.NODE_ENV === 'test';

module.exports = {
    "presets": [
        "@babel/preset-react",
        [
            "@babel/preset-env",
            {
                "modules": isTest && 'commonjs',
                "targets": {
                    "node": true
                }
            }
        ],
        '@babel/preset-typescript'
    ],
    "plugins": [
        "@babel/plugin-transform-react-constant-elements",
        "@babel/plugin-transform-runtime"
    ]
}
