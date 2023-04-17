const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer:{
    proxy:{
      '/api':{
        // target: 'http://34.201.165.165:5000/',
        // target: 'https://3bynfupmn3.execute-api.us-east-1.amazonaws.com/dev',
        target: 'http://192.168.2.14:5051/',
        changeOrigin: true,
        pathRewrite: {
          '^/api': ''
        }
      }
    }
  }
})
