export default {
    "env": {
        "browser": true,
        "es2021": true,
        "node": true
    },
    "extends": [
        "eslint:recommended",
        "plugin:@typescript-eslint/recommended"
    ],
    "parser": "@typescript-eslint/parser",
    "parserOptions": {
        "ecmaVersion": 12,
        "sourceType": "module",
        "project": "./tsconfig.json" // Ensure you have a tsconfig.json file in your project
    },
    "plugins": [
        "@typescript-eslint"
    ],
    "overrides": [
        {
            "files": ["*.ts", "*.tsx"],
            "rules": {
                "require-atomic-updates": "off",
                "no-shadow": "off",
                "@typescript-eslint/no-shadow": ["error"],
                "jest/expect-expect": [
                    "error",
                    { "assertFunctionNames": ["expect", "fc.assert"] }
                ],
                "testing-library/no-node-access": "off",
                "testing-library/render-result-naming-convention": "off",
                "yoda": "warn",
                "no-sequences": "error",
                "no-return-await": "warn",
                "no-await-in-loop": "warn",
                "no-loss-of-precision": "warn",
                "no-promise-executor-return": "warn",
                "no-template-curly-in-string": "warn",
                "no-alert": "warn",
                "no-implicit-globals": "warn",
                "no-labels": "warn",
                "@typescript-eslint/no-explicit-any": "off",
                "no-loop-func": "warn",
                "no-new-wrappers": "warn",
                "no-new": "warn",
                "no-useless-concat": "warn",
                "radix": "error",
                "wrap-iife": "off",
                "@typescript-eslint/array-type": "warn",
                "@typescript-eslint/method-signature-style": "error",
                "curly": "warn",
                "complexity": "off",
                "@typescript-eslint/no-unused-vars": "warn",
                "prefer-template": "warn",
                "@typescript-eslint/no-use-before-define": "off",
                "@typescript-eslint/triple-slash-reference": "off"
            }
        },
    ],
    "rules": {},
    "ignorePatterns": [
        "tslint.json",  // Ignore the TSLint configuration file
        "node_modules/", // Ignore the node_modules directory
        "dist/",        // Ignore the dist directory (commonly used for build outputs)
        "*.d.ts"        // Ignore TypeScript declaration files
    ]
};
