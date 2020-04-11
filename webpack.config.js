const path = require('path');
// https://github.com/babel/babel/issues/7824
require("babel-polyfill");

module.exports = {
  entry: ['babel-polyfill', './webapp/jsx/main.js'],
  output: {
    path: path.resolve(__dirname, 'webapp/js'),
    filename: 'bundle.js'
  },
  module: {
    rules: [

      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
              presets: [
                  "@babel/preset-env",
                  "@babel/preset-react"
              ],
              plugins: [
                  "@babel/plugin-proposal-class-properties"
              ]
          }
        }
      },

        {
          test: /\.(scss)$/,
          use: [
            {
              // adds css to the dom by injecting a <style> tag
              loader: 'style-loader'
            },
            {
               // interprets @import and url() like import/require
               // and will resolve them
               loader: 'css-loader'
            },
            {
               // loader for webpack to process css & scss
               loader: 'postcss-loader',
               options: {
                 plugins: function() {
                   return [ require('autoprefixer')];
                  }
               }
            },
            {
              // loads a sass/scss file & compiles it to css
              loader: 'sass-loader'
            }
          ]
        }
    ]
  }
};
