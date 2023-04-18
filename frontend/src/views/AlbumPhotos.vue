<template>
    <div>
        <h1>
            You are in the Album: &nbsp;&nbsp;&nbsp;{{ albumName }}
        </h1>
        <el-row>
            <el-col>
                <div style="float: left">
                    <el-button type="primary" slot="append" icon="el-icon-plus" @click="addPhoto">add new
                        photo</el-button>
                </div>
            </el-col>
            <br><br><br>
            <el-col :span="6">
                <div style="float: left">
                    <el-input v-model="search" style="width:200px"></el-input>
                    &nbsp;&nbsp;&nbsp;&nbsp;
                    <el-button type="primary" slot="append" icon="el-icon-search" @click="searchAlbum()" v-loading.fullscreen.lock="loading" element-loading-text="Searching">search</el-button>
                </div>
            </el-col>
            <br> <br><br>
            <el-col :span="6" v-for="(photo, index) in photoAlbums" :key="index">
                <el-card class="photo-card">
                    <el-image style="width: 100%; height: 250px; " :src="photo.url" :preview-src-list="photoList"
                        fit="contain">
                    </el-image>
                    <el-button class="button" icon="el-icon-delete" circle @click="deleteImage(photo.name)"></el-button>
                </el-card>
            </el-col>
        </el-row>
        <el-dialog title="add a new photo" :visible.sync="visible.addNewPhoto" @closed="cancelSubmit()">
            <el-form label-width="auto">
                <el-form-item label="album name" prop="name">
                    <el-input v-model="albumName" :disabled="true"></el-input>
                </el-form-item>
                <el-upload ref="child" action="#" list-type="picture-card" :auto-upload="false"
                    :class="{ hideUpload: uploadInfo.hideUploadEdit }"
                    :on-change="(file, fileList) => handlePicChange(file, fileList)">
                    <i slot="default" class="el-icon-plus"></i>
                    <div slot="file" slot-scope="{file}">
                        <img class="el-upload-list__item-thumbnail" :src="file.url" alt="">
                        <span class="el-upload-list__item-actions">
                            <span v-if="!uploadInfo.disabled" class="el-upload-list__item-delete"
                                @click="handlePicRemove()">
                                <i class="el-icon-delete"></i>
                            </span>
                        </span>
                    </div>
                </el-upload>


            </el-form>
            <span slot="footer" class="dialog-footer">
                <el-button @click="cancelSubmit">cancel</el-button>
                <el-button type="primary" @click="submitPhoto">submit</el-button>
            </span>
        </el-dialog>
        <el-dialog :visible.sync="uploadInfo.dialogVisible">
            <img width="100%" :src="uploadInfo.dialogImageUrl" alt="">
        </el-dialog>
    </div>
</template>

<script>
import axios from 'axios';
import AWS from 'aws-sdk';
export default {
    data() {
        return {
            albumName: '',
            photoOriginal: [],
            photoList: [],
            photoAlbums: [],
            visible: {
                addNewPhoto: false
            },
            uploadInfo: {
                disabled: false,
                lengthLimit: 1,
                hideUploadEdit: false,
                dialogVisible: false,
                dialogImageUrl: ''
            },
            search: '',
            file: null,
            userName: '',
            loading: false
        }
    },
    created() {
        console.log(this.$route.query);
        this.albumName = this.$route.query.albumName;
        this.userName = this.$route.query.userName;
        const photoOriginal = localStorage.getItem('photoOriginal');
        if(photoOriginal){
            this.photoOriginal = Array.from(JSON.parse(photoOriginal));
            console.log(this.photoOriginal);
            // this.photoOriginal = this.photoOriginal.filter((v) => {
            //     return v !== '[' && v !== ']';
            // })
            // console.log(this.photoOriginal);
        }
        this.getAlbumPhotos();
        AWS.config.update({
            accessKeyId: 'AKIAVW4WDBYWM3DT23W7',
            secretAccessKey: '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',
            region: 'us-east-1'
        })
    },
    beforeUpdate() {
        localStorage.setItem('photoOriginal', JSON.stringify(this.$data.photoOriginal));
    },
    methods: {
        getAlbumPhotos() {
            let form = new FormData();
            form.append('album', this.albumName)
            axios.post('/api/display_album', form).then((response) => {
                if (response.status === 200) {
                    console.log(response);
                    response.data.images.forEach((v) => {
                        let name = v.name.substring(4);
                        console.log(this.photoOriginal);
                        let url = ''
                        for (let i = 0; i < this.photoOriginal.length; i++) {
                            console.log(this.photoOriginal[i]);
                            if (this.photoOriginal[i].name === name) {
                                url = this.photoOriginal[i].url;
                            }
                        }
                        this.photoAlbums.push({
                            'url': url,
                            'name': name
                        })
                        this.photoList.push(url)
                    })
                    console.log(this.photoAlbums);
                } else {
                    this.$message.error(response.data.message);
                }
            });
        },
        addPhoto() {
            this.visible.addNewPhoto = true;
        },
        handlePicChange(file, fileList) {
            console.log(fileList);
            let rawFile = file.raw
            const isValid = (rawFile.type === 'image/jpeg' || rawFile.type === 'image/png' || rawFile.type === 'image/gif' || rawFile.type === 'image/bmp' || rawFile.type === 'image/webp');
            if (!isValid) {
                this.$message.error('Image format is not correct!, please choose jpg/png/gif/bmp/webp format image!');
                this.$refs.child.clearFiles();
                return false;
            }
            this.file = rawFile;
            this.uploadInfo.hideUploadEdit = (fileList.length >= this.uploadInfo.lengthLimit);

            return isValid;
        },
        handlePicRemove() {
            console.log(this.$refs.child.uploadFiles);
            let fileList = this.$refs.child.uploadFiles;
            fileList.pop();
            this.uploadInfo.hideUploadEdit = (fileList.length >= this.uploadInfo.lengthLimit);
        },
        cancelSubmit() {
            this.$refs.child.clearFiles();
            this.uploadInfo.hideUploadEdit = false;
        },
        submitPhoto() {
            if (this.$refs.child.uploadFiles.length !== 0) {
                let file = this.$refs.child.uploadFiles[0];
                let s3 = new AWS.S3();
                let bucketName = this.userName + '-' + this.albumName + '-manual-images';
                let params = {
                    Bucket: bucketName,
                    Key: file.name,
                    Body: file.raw,
                    ContentType: file.raw.type,
                    ACL: 'public-read'
                };
                console.log(params);
                s3.upload(params, (err, data) => {
                    if (err) {
                        console.log(err);
                        this.$message.warning('Fail to upload!')
                    } else {
                        console.log(data);
                        this.$refs.child.uploadFiles.pop();
                        this.uploadInfo.hideUploadEdit = (this.$refs.child.uploadFiles.length >= this.uploadInfo.lengthLimit);
                        this.visible.addNewPhoto = false;
                        this.$message.success('Upload successfully to s3!');
                        console.log(this.photoOriginal);
                        this.photoOriginal.push({
                            'name': data.Key,
                            'url': data.Location
                        })
                        console.log(this.photoOriginal);
                        this.photoAlbums.push({
                            'url': data.Location,
                            'name': data.Key
                        })
                        this.photoList.push(data.Location)
                        let form = new FormData()
                        form.append('album', this.albumName);
                        form.append('image', JSON.stringify(file))
                        axios.post('/api/upload_image', form, { headers: { 'Content-Type': 'multipart/form-data' } })
                            .then(res => {
                                console.log('upload request return info:', res);
                                if (res.status == 200) {
                                    this.$refs.child.uploadFiles.pop();
                                    this.uploadInfo.hideUploadEdit = (this.$refs.child.uploadFiles.length >= this.uploadInfo.lengthLimit);
                                    this.$message.success('Upload successfully to db!');
                                } else {
                                    this.$message.warning('Fail to upload!')
                                }
                            })
                            .catch(error => {
                                this.$message.warning(error);
                            })
                    }
                })
            }
            else {
                this.$message.warning('Image is empty, please choose one image!');
            }
        },
        handlePictureCardPreview(photo) {
            this.uploadInfo.dialogImageUrl = photo;
            this.uploadInfo.dialogVisible = true;
        },
        deleteImage(name) {
            this.$confirm('Are you sure to delete this photo?', 'Warning', {
                confirmButtonText: 'OK',
                cancelButtonText: 'Cancel',
                type: 'warning'
            }).then(() => {
                let form = new FormData()
                form.append('album', this.albumName)
                form.append('name', name)
                console.log('delete image', name);
                axios.post('/api/delete_image', form).then(res => {
                    console.log('delete request return info:', res);
                    if (res.status == 200) {
                        this.$message({
                            type: 'success',
                            message: 'Delete successfully!'
                        });
                        this.uploadInfo.dialogVisible = false;
                        this.photoOriginal = this.photoOriginal.filter((v) => {
                            return v.name !== name;
                        })
                    } else {
                        this.$message.warning('Fail to delete!')
                    }
                }).catch(error => {
                    this.$message.warning(error);
                }
                )
            }).catch(() => {
                this.$message({
                    type: 'info',
                    message: 'Delete canceled'
                });
            });
        },
        searchAlbum() {
            console.log(this.search);
            if (this.search === '') {
                this.$message.warning("Please input the search content!");
            }
            else {
                console.log(this.search);
                this.loading = true;
                let labelList = this.search.split(' ');
                let form = new FormData();
                form.append('album', this.albumName)
                form.append('labels', labelList)
                axios.post('/api/sage_display_album', form).then(res => {
                    if (res.status === 200) {
                        this.photoAlbums = [];
                        res.data.images.forEach((v) => {
                        let name = v.name;
                        for (let i = 0; i < this.photoOriginal.length; i++) {
                            if (this.photoOriginal[i].name === name) {
                                this.photoAlbums.push({
                                    'url': this.photoOriginal[i].url,
                                    'name': name
                                })
                                this.photoList.push(this.photoOriginal[i].url)
                                break;
                            }
                        }
                        // let url = this.photoOriginal.forEach((item) => {
                        //     if (item.name === name) {
                        //         return v.url;
                        //     }
                        // })
                        // this.photoAlbums.push({
                        //     'url': url,
                        //     'name': name
                        // })
                        // this.photoList.push(url)
                    })
                    }
                    this.loading = false;
                }).catch(error => {
                    this.$message.warning(error);
                    this.loading = false;
                })
            }
        },

    },
}
</script>

<style>
.hideUpload .el-upload.el-upload--picture-card {
    display: none;
}

.photo-card {
    width: 250px;
    height: 350px;
    align-items: center;
}

.button {
    margin-bottom: 10px;
    float: right;
}
</style>