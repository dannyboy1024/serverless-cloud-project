<template>
    <el-card class="box-card">
        <div slot="header" class="clearfix">
            <span>register</span>
        </div>
        <el-form :model="registerForm" :rules="rules" ref="registerForm" label-width="auto" v-loading="loading">
            <el-form-item label="username" prop="username" >
                <el-input v-model="registerForm.username" ></el-input>
            </el-form-item>
            <el-form-item label="password" prop="password">
                <el-input type="password" v-model="registerForm.password"></el-input>
            </el-form-item>
            <el-form-item label="confirm password" prop="confirmPassword">
                <el-input type="password" v-model="registerForm.confirmPassword" ></el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="register">register</el-button>
            </el-form-item>
            <el-form-item class="position:right">
                            </el-form-item>
           
            </el-form>
            <el-button type="text" style="position: absolute; right: 5%; bottom: 5%;" @click="login">log in</el-button>
            <br>
    </el-card>
</template>
<script>
import axios from 'axios';
    export default {
        data() {
            return {
                registerForm: {
                    username: '',
                    password: '',
                    confirmPassword: ''
                },
                rules: {
                    username: [
                        { required: true, message: 'please input user name', trigger: 'blur' }
                    ],
                    password: [
                        { required: true, message: 'please input password', trigger: 'blur' }
                    ],
                    confirmPassword: [
                        { required: true, message: 'please input password again', trigger: 'blur' }
                    ]
                },
                loading: false
            }
        },
        methods: {
            register() {
                this.$refs.registerForm.validate((valid) => {
                    this.loading = true;
                    if (valid) {
                        if (this.registerForm.password !== this.registerForm.confirmPassword) {
                            this.$message.error('passwords do not match');
                            this.loading = false;
                            return false;
                        }
                        console.log(this.registerForm);
                        let form = new FormData();
                        form.append('username',this.registerForm.username);
                        form.append('password',this.registerForm.password);
                        axios.post(
                           '/api/register',form, {headers:{'Content-Type': 'multipart/form-data'}}
                        ).then((response) => {
                            console.log(response);
                            if (response.status === 200) {
                                this.$message({
                                    message: 'sucessfully registered',
                                    type: 'success'
                                });
                                this.$router.push({ path: '/dashboard' , params : {username: this.registerForm.username}});
                            } else {
                                this.$message.error(response.data.message);
                                this.loading = false;
                            }
                        })
                        .catch((error) => {
                            console.log(error);
                            this.$message.error(error);
                        });
                    } 
                        this.loading = false;
                        return false;
                });
            },
            login() {
                this.$router.push({ path: '/' });
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

