# serverless-cloud-project
Overview:
    - A website of pictures
    - Home page (Frontend)
        Register / Login
    - Main page (Frontend)
        - Users start with a Default album
        - Manually create albums
        - Automatically create albums
        - Showing a list of albums on the left of the screen maybe
        - Choose an album and display one or all images
        - Choose an album and display images according to image items
    - Admin interface (Using backend url)
        - Display charts

# Backend routes for Frontend
1.  /upload_image
    req = {
        'album' : # Album name [String]
        'image' : # Image content [Same as A2]
    }
    resp = {
        'success' : # success / fail [Boolean] 
        'album'   : # Album name [String]
    }

2.  /display_image
    req = {
        'album' : # Album name [String]
        'name'  : # Image name [String]
    }
    resp = {
        'success' : # success / fail [Boolean] 
        'image'   : # Image content and Image Name [{content, name}]
    }

3.  /delete_image
    req = {
        'album' : # Album name [String]
        'name'  : # Image name [String]        
    }
    resp = {
        'success' : # success / fail [Boolean]       
    }

4.  /create_album
    req = {
        'album' : # Album name [String]
    }
    resp = {
        'success' : # success / fail [Boolean]
    }

5.  /sage_create_albums
    req = {
        'isAuto' : # Is in Automatic mode ? [Boolean]
    }
    resp = {
        'covers' : [
            {
                'albumName' : # album name  [String]
                'coverImage' : # cover image [same as A2]
            },
            ...
        ] [List]
    }

6.  /get_album_names
    req = {
        # None
    }
    resp = {
        'covers' : [
            {
                'albumName' : # album name  [String]
                'coverImage' : # cover image [same as A2]
            },
            ...
        ] [List]
    }

7.  /display_album
    req = {
        'album' : # Album name [String]
    }
    resp = {
        'images' : # All the images in the album [List]
    }

8.  /sage_display_album
    req = {
        'album'  : # Album name [String]
        'labels' : # List of lables [List] 
    }
    resp = {
        'images' : # Only the images in the album with the given labels [List]
    }

9. /delete_album
    req = {
        'album'  : # Album name [String]
    }
    resp = {
        'success' : # success / fail [Boolean]
    }

10. /register
    req = {
        'id'       : # Account name [String]
        'password' : # Password     [String]
    }
    resp = {
        'success' : # success / fail [Boolean]
    }

11. /login
    req = {
        'id'       : # Account name [String]
        'password' : # Password     [String]
    }
    resp = {
        'success' : # success / fail [Boolean]
    }

12. /logout
    req = {
        'id'       : # Account name [String]
        'password' : # Password     [String]
    }
    resp = {
        'success' : # success / fail [Boolean]
    }

13. /overwrite_manual_albums
    req = {
        # None
    }
    resp = {
        'success' : # success / fail [Boolean] 
    }
