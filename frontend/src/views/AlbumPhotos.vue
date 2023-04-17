<template>
    <div>
        <h1>
            {{ albumName }}
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
                    <el-button type="primary" slot="append" icon="el-icon-search" @click="searchAlbum()">search</el-button>
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
            userName: ''
        }
    },
    created() {
        console.log(this.$route.query);
        this.albumName = this.$route.query.albumName;
        this.userName = this.$route.query.userName;
        this.getAlbumPhotos();
        AWS.config.update({
            accessKeyId: 'AKIAVW4WDBYWM3DT23W7',
            secretAccessKey: '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',
            region: 'us-east-1'
        })
    },
    methods: {
        getAlbumPhotos() {
            let form = new FormData();
            form.append('album', this.albumName)
            axios.post('/api/display_album', form).then((response) => {
                if (response.status === 200) {
                    console.log(response);
                    response.data.images.forEach((v) => {
                        let content = eval('(' + v.content + ')');
                        this.photoAlbums.push({
                            'url': content.url,
                            'name': content.name
                        })
                        this.photoList.push(content.url)
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
        // submitPhoto() {
        //     console.log(this.$refs.child.uploadFiles);
        //     if (this.$refs.child.uploadFiles.length !== 0) {
        //         let form = new FormData()
        //         form.append('album', this.albumName);
        //         let file = this.$refs.child.uploadFiles[0];
        //         console.log(this.$refs.child.uploadFiles[0]);
        //         // form.append('image', JSON.stringify(file))
        //         console.log(this.file);
        //         form.append('image', this.file)
        //         console.log(JSON.stringify(form));
        //         axios.post('/api/upload_image', form, { headers: { 'Content-Type': 'multipart/form-data' } })
        //             .then(res => {
        //                 console.log('upload request return info:', res);
        //                 if (res.status == 200) {
        //                     this.$refs.child.uploadFiles.pop();
        //                     this.uploadInfo.hideUploadEdit = (this.$refs.child.uploadFiles.length >= this.uploadInfo.lengthLimit);
        //                     this.visible.addNewPhoto = false;
        //                     this.$message.success('Upload successfully!');
        //                     this.photoAlbums.push({
        //                         'url': file.url,
        //                         'name': file.name
        //                     })
        //                 } else {
        //                     this.$message.warning('Fail to upload!')
        //                 }
        //             })
        //             .catch(error => {
        //                 this.$message.warning(error);
        //             })
        //     } else {
        //         this.$message.warning('Image is empty, please choose one image!');
        //     }
        // },
        submitPhoto() {
            if (this.$refs.child.uploadFiles.length !== 0) {
                let file = this.$refs.child.uploadFiles[0];
                let s3 = new AWS.S3();
                let bucketName = this.userName + '-' + this.albumName + '-manual-images';
                let params = {
                    Bucket: bucketName,
                    Key: file.name,
                    Body: file.raw,
                    ContentType: file.raw.type
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
                        this.photoAlbums.push({
                            'url': file.url,
                            'name': file.name
                        })
                        let form = new FormData()
                        form.append('album', this.albumName);
                        form.append('image', JSON.stringify(file))
                        axios.post('/api/upload_image', form, { headers: { 'Content-Type': 'multipart/form-data' } })
                            .then(res => {
                                console.log('upload request return info:', res);
                                if (res.status == 200) {
                                    this.$refs.child.uploadFiles.pop();
                                    this.uploadInfo.hideUploadEdit = (this.$refs.child.uploadFiles.length >= this.uploadInfo.lengthLimit);
                                    this.visible.addNewPhoto = false;
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
                        this.photoAlbums = this.photoAlbums.filter((v) => {
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
                let labelList = this.search.split(' ');
                let form = new FormData();
                form.append('album', this.albumName)
                form.append('labels', labelList)
                axios.post('/api/sage_display_album', form).then(res => {
                    if (res.status === 200) {
                        response.data.images.forEach((v) => {
                        let content = eval('(' + v.content + ')');
                        this.photoAlbums.push({
                            'url': content.url,
                            'name': content.name
                        })
                        this.photoList.push(content.url)
                    })
                    }
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