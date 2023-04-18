<template>
    <el-card class="box-card">
        <div slot="header" class="clearfix">
            <h2 >YourSmartAlbum</h2>
            <br>
            <span>log in</span>
        </div>
        <el-form :model="loginForm" :rules="rules" ref="loginForm" label-width="auto" v-loading="loading">
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
                },
                loading : false
            }
        },
        methods: {
            login() {
                this.$refs.loginForm.validate((valid) => {
                    if (valid) {
                        this.loading = true;
                        let form = new FormData();
                        form.append('username', this.loginForm.username);
                        form.append('password', this.loginForm.password);
                        axios.post('/api/login', form).then((response) => {
                            if (response.status === 200) {
                                this.$message({
                                    message: 'sucessfully logged in',
                                    type: 'success'
                                });
                                console.log(this.loginForm.username);
                                this.$router.push({ path: '/dashboard' , query : {username: this.loginForm.username}});
                            } else {
                                this.$message.error(response.message);
                            }
                            this.loading = false;
                        }).catch((error) => {
                            this.$message.error(error.message);
                            this.loading = false;
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

