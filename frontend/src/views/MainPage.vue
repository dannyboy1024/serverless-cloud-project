<template>
    <div>
        <el-row>
            <h2 style="position: absolute;top:-50px; left:10px">
                Hi, {{ this.userName }}
            </h2>
            <el-button style="position: absolute;top:-30px; right:10px" @click="logout">logout</el-button>
        </el-row>
        <el-row style="display: flex; align-items: center;">
            <el-col :span="10">
                <div>
                    <h3 style="text-align: left;"> &nbsp;&nbsp;&nbsp; Below are Your albums, come and create your own album!
                    </h3>
                </div>
            </el-col>
            <el-col :span="8">
                <el-button type="primary" icon="el-icon-plus" @click="addAlbum">add new
                    album</el-button>
            </el-col>
        </el-row>
        <el-row>
            <el-col>
                <div style="float: left">
                    &nbsp;&nbsp;{{ this.textContent }}&nbsp;
                    <el-tooltip placement="top" :content="tipContent">
                        <el-switch v-model="auto" active-color="#13ce66" inactive-color="#ff4949" @change="autoChange()" v-loading.fullscreen.lock="loading" :element-loading-text="loadingText">
                        </el-switch>
                    </el-tooltip>
                </div>

            </el-col>
            <!-- <el-col v-if="this.auto == true">
                        <div style="float:left">
                            Want to overwrite the old album? &nbsp;
                            <el-button type="success" icon="el-icon-check" circle @click="rewrite()"></el-button>
                        </div>
                    </el-col> -->
            <br><br><br>
            <el-col :span="5" v-for="(album, index) in photoAlbums" :key="album.albumName" :offset="index > 0 ? 0 : 2">
                <el-card class="box-card" :body-style="{ padding: '0px' }">
                    <el-image style="width: 100%; height: 250px" :src="album.coverImage" fit="contain"
                        v-if="album.coverImage"> </el-image>
                    <el-image style="width: 100%; height: 250px" v-else :src="require('../assets/fail.png')" fit="contain">
                    </el-image>
                    <div style="padding: 14px;">
                        <span>{{ album.albumName }}</span>
                        <div class="bottom clearfix">
                            <el-button style="position: relative; float:left" circle icon="el-icon-delete"
                                @click="deleteAlbum(album.albumName)" v-loading.fullscreen.lock="loading"
                                :element-loading-text="loadingText"></el-button>
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

        <el-dialog title="add a new ablum" :visible.sync="visible.addNewDialog" @closed="cancelUpload">
            <el-form :model="form" ref="form" label-width="auto" class="demo-ruleForm">
                <el-form-item label="album name" prop="name">
                    <el-input v-model="form.name"></el-input>
                </el-form-item>
            </el-form>
            <span slot="footer" class="dialog-footer">
                <el-button @click="cancelUpload">cancel</el-button>
                <el-button type="primary" @click="submitAlbum" v-loading.fullscreen.lock="loading"
                    :element-loading-text="loadingText">submit</el-button>
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
            loading: false,
            tipContent: 'Click the switch to enable auto categorize, and the system will automatically categorize your photos into different albums.',
            loadingText: '',
            photoOriginal: []
        }
    },

    methods: {
        initPhoteAbulm() {
            axios.get('/api/get_album_names').then((response) => {
                if (response.status === 200) {
                    console.log(response);
                    let data = response.data.covers;
                    data.forEach((item) => {
                        let url = ''
                        if (item.coverImage) {
                            let imageName = item.coverImage.substring(4)
                            for (let i = 0; i < this.photoOriginal.length; i++) {
                                if (imageName === this.photoOriginal[i].name) {
                                    url = this.photoOriginal[i].url;
                                    break;
                                }
                            }
                        }
                        this.photoAlbums.push({
                            albumName: item.albumName,
                            coverImage: url
                        });
                    });
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
                this.loadingText = 'submitting the album...';
                this.loading = true;
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
                    this.loading = false;
                }).catch((error) => {
                    this.$message.error(error);
                    this.loading = false;
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
                // this.initPhoteAbulm();
                location.reload();
                this.textContent = 'Need auto categorize?'
                this.tipContent = 'Click the switch to enable auto categorize, and the system will automatically categorize your photos into different albums.'
            }
            let form = new FormData();
            form.append('isAuto', this.auto);
            if (this.auto == true) {
                this.loading = true;
                this.loadingText = 'auto categorizing...';
                axios.post(
                    '/api/sage_create_albums', form
                ).then((response) => {
                    if (response.status === 200) {
                        let data = response.data;
                        this.photoAlbums = [];
                        data.covers.forEach((item) => {
                            let url = ''
                            if (item.coverImage) {
                                let imageName = item.coverImage.substring(4)
                                for (let i = 0; i < this.photoOriginal.length; i++) {
                                    if (imageName === this.photoOriginal[i].name) {
                                        url = this.photoOriginal[i].url;
                                        break;
                                    }
                                }
                            }
                            this.photoAlbums.push({
                                albumName: item.albumName,
                                coverImage: url
                            });
                        });
                        this.$message({
                            message: 'sucessfully auto categorize albums',
                            type: 'success'
                        });
                    } else {
                        this.$message.error(response.data.message);
                    }
                    this.loading = false;
                }).catch((error) => {
                    this.$message.error(error);
                    this.loading = false;
                });
                this.textContent = 'Need change back to original albums?'
                this.tipContent = 'Switch to original albums'
            }
        },
        rewrite() {
            axios.get('/api/overwrite_manual_albums').then((response) => {
                if (response.status === 200) {
                    this.$message({
                        message: 'sucessfully rewrite albums',
                        type: 'success'
                    });
                    this.initPhoteAbulm();
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
                this.loadingText = 'deleting the album...';
                this.loading = true;
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
                        this.photoAlbums.filter((item) => {
                            return item.name !== albumName;
                        });
                        location.reload();
                    } else {
                        this.$message.error(response.data.message);
                    }
                    this.loading = false;
                });
            }).catch(() => {
                this.$message({
                    type: 'info',
                    message: 'Delete canceled'
                });
                this.loading = false;
            });

        }
    },
    created() {
        console.log(this.$route.query);
        this.userName = this.$route.query.username;
        const photoOriginal = localStorage.getItem('photoOriginal');
        if (photoOriginal) {
            this.photoOriginal = Array.from(JSON.parse(photoOriginal));
            console.log(this.photoOriginal);
        }
        this.initPhoteAbulm();
    },
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