/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-disable no-undef */
const path = require('path')
const ESLintPlugin = require('eslint-webpack-plugin')
const Dotenv = require('dotenv-webpack')
const TerserPlugin = require('terser-webpack-plugin')

const environment = process.env.NODE_ENV
const environmentMapping = {
	production: 'production',
	development: 'development',
}

// const isProd = environmentMapping[environment] === 'production'
const isDev = environmentMapping[environment] === 'development'
// webpack only allows development or production mode, so we need the below check
const useStagingEnv = process.env.ENV_MODE === 'staging'

const devBuildPath = path.resolve(__dirname, '../backend/static')
const prodBuildPath = path.resolve(__dirname, './dist/')

module.exports = {
	entry: './src/index.js',
	plugins: [
		new ESLintPlugin({
			extensions: ['js', 'jsx', 'ts', 'tsx', 'css'],
			exclude: ['node_modules', 'src/**/*.css'],
			emitError: isDev,
			emitWarning: isDev,
			failOnError: isDev,
		}),
		new Dotenv({
			path: path.resolve(__dirname, '../envs', isDev ? 'development.env':
				useStagingEnv ? 'staging.env' : 'production.env')
		})
	],
	...(isDev && {devtool: 'inline-source-map'}),
	module: {
		rules: [
			{
				test: /\.[tj]sx?$/,
				exclude: [
					path.resolve(__dirname, 'node_modules'),
				],
				use: [
					{
						loader: 'babel-loader',
					},
					// {
					// 	loader: 'ts-loader',
					// },
				],
			},
			{
				test: /\.(s[ac]|c)ss?$/i,
				use: [
					'style-loader',
					'css-loader',
					'postcss-loader',
					'sass-loader'
				],
			},
			{
				test: /\.(png|svg|jpg|jpeg|gif)$/i,
				type: 'asset/resource',
			},
			{
				test: /\.(woff|woff2|eot|ttf|otf)$/i,
				type: 'asset/resource',
			},
		],
	},
	resolve: {
		extensions: ['.tsx', '.ts', '.jsx', '.js'],
		alias: {
			api: path.resolve(__dirname, 'src', 'api'),
			components: path.resolve(__dirname, 'src', 'components'),
			store: path.resolve(__dirname, 'src', 'store'),
			pages: path.resolve(__dirname, 'src', 'pages'),
			src: path.resolve(__dirname, 'src'),
		},
	},
	mode: environment ? environmentMapping[environment] : 'production',
	optimization: {
		minimize: true,
		minimizer: [new TerserPlugin()],
	},
	output: {
		filename: '[name].js',
		path: isDev ? devBuildPath : prodBuildPath,
	},
}
