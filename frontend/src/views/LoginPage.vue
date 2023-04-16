<template>
    <el-card class="box-card">
        <div slot="header" class="clearfix">
            <span>log in</span>
        </div>
        <el-form :model="loginForm" :rules="rules" ref="loginForm" label-width="auto">
            <el-form-item label="username" prop="username">
                <el-input v-model="loginForm.username"></el-input>
            </el-form-item>
            <el-form-item label="password" prop="password">
                <el-input type="password" v-model="loginForm.password"></el-input>
            </el-form-item>
            
            <el-form-item>
                <el-button type="primary" @click="login">log in</el-button>
            </el-form-item>
        </el-form>
        <el-button type="text" style="position: absolute; right: 5%; bottom: 5%;" @click="register">register</el-button>
            <br>
    </el-card>
</template>

<script>
import axios from 'axios';
    export default {
        data() {
            return {
                loginForm: {
                    username: '',
                    password: ''
                },
                rules: {
                    username: [
                        { required: true, message: 'please input user name', trigger: 'blur' }
                    ],
                    password: [
                        { required: true, message: 'please input password', trigger: 'blur' }
                    ]
                }
            }
        },
        methods: {
            login() {
                this.$refs.loginForm.validate((valid) => {
                    if (valid) {
                        axios.post('/login', this.loginForm).then((response) => {
                            if (response.status === 200) {
                                this.$message({
                                    message: 'sucessfully logged in',
                                    type: 'success'
                                });
                                this.$router.push({ path: '/dashboard' , params : {username: this.loginForm.username}}, window.location.reload());
                            } else {
                                this.$message.error(response.data.message);
                            }
                        });
                    } else {
                        return false;
                    }
                });
            },
            register() {
                this.$router.push({ path: '/register' });
            }
        }
    }
</script>

<style>
.box-card {
  margin: 0;
  width: 500px;
  display: flex;
  flex-direction: column;
  position: absolute;
top: 50%;
left: 50%;
transform: translate(-50%, -50%);
}
.el-form-item {
  width: 90%;
}
</style>

