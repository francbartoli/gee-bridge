// load the needed node modules
var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

// webpack project settings
module.exports = {
  context: __dirname,
  entry: {
          mapclient: './mapclient/templates/components/map/index',
  },
  output: {
      path: path.resolve('./static/bundles/'),
      filename: "[name]-[hash].js"
  },
  node: {fs: "empty"},

  plugins: [
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NoEmitOnErrorsPlugin(), // don't reload if there is an error
    new BundleTracker({path: __dirname, filename: './webpack-stats.json'})

  ],

    module: {
  loaders: [
    {
      test: /\.(js|jsx)$/,
      exclude: /(node_modules)/,
      loader: 'babel-loader', // 'babel-loader' is also a legal name to reference
      query: {
        presets: ['es2015', 'react'],
        "plugins": ["transform-class-properties"]
      }
    }, {
      test: /\.css$/,
      loader: "style-loader!css-loader"
    }, {
      test: /\.json$/,
      loader: "json-loader"
    }, {
      test: /\.(png|gif|jpg|jpeg|svg|otf|ttf|eot|woff)$/,
      loader: 'file-loader'
    }

  ]
},

  resolve: {
    //modulesDirectories: ['node_modules'],
    modules: [path.resolve(__dirname), "node_modules"],
    extensions: ['*', '.js', '.jsx']
  },
}
