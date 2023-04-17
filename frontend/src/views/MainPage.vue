<template>
    <div>
        <el-row>
            <h3 style="position: absolute;top:-50px; left:10px">
                Hi, {{ this.userName }}
            </h3>
            <el-button style="position: absolute;top:-30px; right:10px" @click="logout">logout</el-button>
        </el-row>
        <el-tabs v-model="activeName" @tab-click="handleClick">
            <el-tab-pane label="Home Page" name="first">first</el-tab-pane>
            <el-tab-pane label="Alblum" name="second">
                <el-row>
                    <el-col>
                        <div style="float: left">
                            &nbsp;&nbsp;{{ this.textContent }}&nbsp;
                            <el-switch v-model="auto" active-color="#13ce66" inactive-color="#ff4949"
                                @change="autoChange()">
                            </el-switch>
                        </div>
                        <div style="float: right">
                            <el-button type="primary" slot="append" icon="el-icon-plus" @click="addAlbum">add new
                                album</el-button>
                        </div>
                    </el-col>
                    <el-col v-if="this.auto == true">
                        Want to overwrite the old album? &nbsp;
                        <el-button type="success" round @click="rewrite()"></el-button>
                    </el-col>
                    <br><br><br>
                    <el-col :span="5" v-for="(album, index) in photoAlbums" :key="album.albumName"
                        :offset="index > 0 ? 0 : 2">
                        <el-card class="box-card" :body-style="{ padding: '0px' }">
                            <el-image style="width: 100%; height: 250px" :src="album.coverImage" fit="contain"
                                v-if="album.coverImage"> </el-image>
                            <el-image style="width: 100%; height: 250px" v-else :src="require('../assets/fail.png')"
                                fit="contain">
                            </el-image>
                            <div style="padding: 14px;">
                                <span>{{ album.albumName }}</span>
                                <div class="bottom clearfix">
                                    <el-button style="position: relative; float:left" circle icon="el-icon-delete"
                                        @click="deleteAlbum(album.albumName)"></el-button>
                                    <router-link class="router" target="_blank"
                                        :to="{ name: 'AlbumPhotos', query: { albumName: album.albumName, userName: userName } }">
                                        open
                                    </router-link>
                                </div>
                            </div>

                        </el-card>
                    </el-col>
                    <br><br><br>
                </el-row>
            </el-tab-pane>
            <el-tab-pane label="Manage Alblum" name="third">third</el-tab-pane>
        </el-tabs>
        <el-dialog title="add a new ablum" :visible.sync="visible.addNewDialog" @closed="cancelUpload">
            <el-form :model="form" ref="form" label-width="auto" class="demo-ruleForm">
                <el-form-item label="album name" prop="name">
                    <el-input v-model="form.name"></el-input>
                </el-form-item>
            </el-form>
            <span slot="footer" class="dialog-footer">
                <el-button @click="cancelUpload">cancel</el-button>
                <el-button type="primary" @click="submitAlbum">submit</el-button>
            </span>
        </el-dialog>
    </div>
</template>


<script>
import axios from 'axios';
export default {
    data() {
        return {
            userName: '',
            activeName: 'second',
            searchAlbumName: '',
            visible: {
                addNewDialog: false
            },
            form: {
                name: ''
            },
            photoAlbums: [],
            auto: false,
            textContent: 'Need auto categorize?',
            loading: false
        }
    },
    methods: {
        initPhoteAbulm() {
            axios.get('/api/get_album_names').then((response) => {
                if (response.status === 200) {
                    console.log(response);
                    this.photoAlbums = response.data.covers;
                } else {
                    this.$message.error(response.data.message);
                }
            });
            console.log(this.$route.params.albumName);
            // this.photoAlbums = [
            //     {
            //         name: 'album1',
            //         cover: ''
            //     },
            //     {
            //         name: 'album2',
            //         cover: 'https://shadow.elemecdn.com/app/element/hamburger.9cf7b091-55e9-11e9-a976-7f4d0b07eef6.png'
            //     },
            //     {
            //         name: 'album3',
            //         cover: 'https://fuss10.elemecdn.com/e/5d/4a731a90594a4af544c0c25941171jpeg.jpeg'
            //     },
            //     {
            //         name: 'album4',
            //         cover: 'https://shadow.elemecdn.com/app/element/hamburger.9cf7b091-55e9-11e9-a976-7f4d0b07eef6.png'
            //     },
            // ]
        },
        handleClick(tab, event) {
            console.log(tab, event);
        },
        addAlbum() {
            this.visible.addNewDialog = true;
        },
        searchAlbum() {
            console.log(this.searchAlbumName);
        },
        submitAlbum() {
            if (this.form.name === '') {
                this.$message.error('please input album name');
                return;
            } else {
                let form = new FormData();
                form.append('album', this.form.name);
                axios.post(
                    '/api/create_album', form, { headers: { 'Content-Type': 'multipart/form-data' } }
                ).then((response) => {
                    if (response.status === 200) {
                        this.$message({
                            message: 'sucessfully add a new album',
                            type: 'success'
                        });
                        this.visible.addNewDialog = false;
                        this.initPhoteAbulm();
                        location.reload();
                    } else {
                        this.$message.error(response.data.message);
                    }
                });

            }
        },
        // openAlbum(album) {
        //     console.log(album);
        //     this.$router.push({ path: '/album', query: { 'albumName': album.name } });
        // },
        cancelUpload() {
            this.visible.addNewDialog = false;
            this.form.name = ''
        },
        logout() {
            axios.post('/api/logout').then((response) => {
                if (response.status === 200) {
                    this.$message({
                        message: 'sucessfully logout',
                        type: 'success'
                    });
                    this.$router.push({ path: '/' });
                } else {
                    this.$message.error(response.data.message);
                }
            });
        },
        autoChange() {
            console.log(this.auto);
            if (this.auto == false) {
                this.initPhoteAbulm();
                this.textContent = 'Need auto categorize?'
            }
            let form = new FormData();
            form.append('isAuto', this.auto);
            if (this.auto == true) {
                axios.put(
                    '/api/sage_create_albums', form
                ).then((response) => {
                    if (response.status === 200) {
                        this.$message({
                            message: 'sucessfully auto categorize albums',
                            type: 'success'
                        });
                        this.photoAlbums = response.data.covers;
                    } else {
                        this.$message.error(response.data.message);
                    }
                })
                this.textContent = 'Need change back to original albums?'
            }
        },
        rewrite() {
            axios.put({
                url: '/api/overwrite_manual_albums'
            }).then((response) => {
                if (response.status === 200) {
                    this.$message({
                        message: 'sucessfully rewrite albums',
                        type: 'success'
                    });
                } else {
                    this.$message.error(response.data.message);
                }
            })
        },
        deleteAlbum(albumName) {
            console.log(albumName);
            this.$confirm('This will permanently delete the album. Continue?', 'Warning', {
                confirmButtonText: 'OK',
                cancelButtonText: 'Cancel',
                type: 'warning'
            }).then(() => {
                let form = new FormData();
                form.append('album', albumName);
                axios.post(
                    '/api/delete_album', form
                ).then((response) => {
                    if (response.status === 200) {
                        this.$message({
                            message: 'sucessfully delete album',
                            type: 'success'
                        });
                        this.initPhoteAbulm();
                        location.reload();
                    } else {
                        this.$message.error(response.data.message);
                    }
                });
            }).catch(() => {
                this.$message({
                    type: 'info',
                    message: 'Delete canceled'
                });
            });

        }
    },
    created() {
        console.log(this.$route.query);
        this.userName = this.$route.query.username;
    },
    mounted() {
        this.initPhoteAbulm();
    }
}
</script>

<style>
.box-card {
    width: 250px;
    height: 350px;
}

.router {
    margin-bottom: 10px;
    float: right;
}
</style>