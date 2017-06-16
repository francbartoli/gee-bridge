#!/usr/bin/env python
import ast
import requests
import os
import ee
import sys
from bs4 import BeautifulSoup
import logging
import retrying
import getpass
from urllib import unquote

class DataManagement():
    """Algorithm for managing assets in GEE"""

    # Define URLs
    __GOOGLE_ACCOUNT_URL = 'https://accounts.google.com'
    __AUTHENTICATION_URL = 'https://accounts.google.com/ServiceLoginAuth'
    __APPSPOT_URL = 'https://ee-api.appspot.com/assets/upload/geturl?'

    def __init__(self,usr,pwd): #,local_data,asset_name):

        """Constructor for wpDataManagement"""
        ee.Initialize ()

        self.__username = usr
        self.__password = pwd

        self.logger = logging.getLogger ( "wpWin.DataManagement" )
        self.logger.setLevel ( level=logging.DEBUG )
        formatter = logging.Formatter ( "%(levelname) -4s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s" )

        fh = logging.FileHandler ( 'wapor_gee_datamanagement.log' )
        fh.setLevel ( logging.ERROR )
        fh.setFormatter ( formatter )
        self.logger.addHandler ( fh )

        ch = logging.StreamHandler ( sys.stdout )
        ch.setLevel ( logging.DEBUG )
        ch.setFormatter ( formatter )
        self.logger.addHandler ( ch )

    @property
    def user_name(self):
        return self.__username

    @user_name.setter
    def user_name(self , name):
        self.__username = name

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self , pwd):
        self.__password = pwd

    def create_google_session(self):

        session = requests.session ()
        login_html = session.get ( DataManagement.__GOOGLE_ACCOUNT_URL )

        #Check cookies returned because there is an issue with the authentication
        #GAPS , GALX , NID - These cookies are used to identify the user when using Google + functionality.
        #GAPS is still provided
        self.logger.debug(session.cookies.get_dict ().keys ())
        try:
            galx = session.cookies['GALX']
        except:
            self.logger.error('No cookie GALX')

        soup_login = BeautifulSoup ( login_html.content , 'html.parser' ).find ( 'form' ).find_all ( 'input' )
        payload = {}
        for u in soup_login:
            if u.has_attr ( 'value' ):
                payload[u['name']] = u['value']

        payload['Email'] = self.__username
        payload['Passwd'] = self.__password

        auto = login_html.headers.get ( 'X-Auto-Login' )
        follow_up = unquote ( unquote ( auto ) ).split ( 'continue=' )[-1]
        #Commented as suggested in https://github.com/tracek/gee_asset_manager/issues/36
        #galx = login_html.cookies['GALX']

        payload['continue'] = follow_up

        # Commented as suggested in https://github.com/tracek/gee_asset_manager/issues/36
        #payload['GALX'] = galx

        session.post ( DataManagement.__AUTHENTICATION_URL , data=payload )
        return session

    def get_assets_info(self, asset_name):

        self.asset_path = 'users/fabiolananotizie/' + asset_name
        # self.asset_path = asset_name

        if ee.data.getInfo ( self.asset_path ):
            self.logger.debug('Collection %s Exists' %  self.asset_path)
        else:
            ee.data.createAsset ( {'type': ee.data.ASSET_TYPE_IMAGE_COLL} ,  self.asset_path )
            self.logger.debug('Collection %s Created' %  self.asset_path)

        assets_list = ee.data.getList ( params={'id':  self.asset_path} )
        assets_names = [os.path.basename ( asset['id'] ) for asset in assets_list]
        return assets_names

    def get_upload_url(self,session):

        r = session.get ( DataManagement.__APPSPOT_URL )
        if r.text.startswith ( '\n<!DOCTYPE html>' ):
            self.logger.debug ( 'Incorrect credentials. Probably. If you are sure the credentials are OK, '
                                'refresh the authentication token. If it did not work report a problem. '
                                'They might have changed something in the Matrix.' )
            sys.exit ( 1 )
        elif r.text.startswith ( '<HTML>' ):
            self.logger.debug ( 'Redirecting to upload URL' )
            r = session.get ( DataManagement.__APPSPOT_URL )
            d = ast.literal_eval ( r.text )

        return d['url']

    def retry_if_ee_error(self,exception):
        return isinstance ( exception , ee.EEException )

    def __delete_image(self,image):
        items_in_destination = ee.data.getList ( {'id': self.asset_path} )
        for item in items_in_destination:
            asset_to_delete = item['id']
            if image in asset_to_delete:
                self.logger.warning ( 'Found %s ' % image )
                ee.data.deleteAsset ( image )

    def __upload_image(self,file_path,session,upload_url,image_name,properties,nodata):
        with open ( file_path , 'rb' ) as f:
            files = {'file': f}
            resp = session.post ( upload_url , files=files )
            gsid = resp.json ()[0]
            asset_data = {"id": image_name ,
                          "tilesets": [
                              {"sources": [
                                  {"primaryPath": gsid ,
                                   "additionalPaths": []}
                              ]}
                          ] ,
                          "bands": [] ,
                          "properties": properties ,
                          "missingData": {"value": nodata}
                          }
            task_id = ee.data.newTaskId ( 1 )[0]
            _ = ee.data.startIngestion ( task_id , asset_data )

    @retrying.retry ( retry_on_exception=retry_if_ee_error , wait_exponential_multiplier=1000 ,
                      wait_exponential_max=4000 , stop_max_attempt_number=3 )
    def data_management(self,session,upload_url,assets_names,file_path, properties, nodata):

        file_root = file_path.split ( "/" )[-1].split ( "." )[0]
        image_name = self.asset_path + '/%s' % file_root

        already_uploaded = False
        if file_root in assets_names:
            self.logger.error("%s already in collection" % file_root)
            already_uploaded = True

        #if name file already in that asset it throws an error
        if os.path.exists ( file_path ) and not already_uploaded:
            self.__upload_image(file_path , session , upload_url , image_name,properties,nodata)
        else:
            self.logger.debug('%s already uploaded in GEE - Deleting old file' % file_root)
            self.__delete_image(image_name)
            self.__upload_image ( file_path , session , upload_url , image_name , properties , nodata )

    def task_management(self):
        pass

def main(argv):

    if len ( argv ) != 1:
        print '\nUser & Password Storage Program v.01\n'
        sys.exit ( 'Usage: wpDataManagement.py <directory_name>' )

    username_gee = raw_input ( 'Please Enter a User Name: ' )
    password_gee = getpass.getpass ( 'Please Enter a Password: ' )

    properties = None
    no_data = None

    #gee_root = 'projects/fao-wapor/'
    #gee_root = 'users/fabiolananotizie/'

    data_management_session = DataManagement ( username_gee , password_gee )
    active_session = data_management_session.create_google_session ()
    upload_url = data_management_session.get_upload_url(active_session)

    path_test = argv[0]
    if os.path.isfile ( path_test ):
        gee_asset = '_'.join (path_test.split('/')[-1].split ( "_" )[0:2] )
        #gee_file = path_test.split('/')[-1].split ( "." )[0]
        present_assets = data_management_session.get_assets_info ( gee_asset )
        data_management_session.data_management ( active_session ,
                                                  upload_url ,
                                                  present_assets ,
                                                  path_test ,
                                                  properties ,
                                                  no_data )
    elif os.path.isdir ( path_test ):
        new_files = []
        root_dir = None
        for (dirpath , dirnames , filenames) in os.walk ( path_test ):
            new_files.extend (filenames )
            root_dir = dirpath
            break

        for each_file in new_files:
            file_temp = root_dir + "/" + each_file
            gee_asset = '_'.join ( each_file.split ( "_" )[0:2] )
            #gee_file = each_file.split ( "." )[0]
            present_assets = data_management_session.get_assets_info (gee_asset)
            data_management_session.data_management ( active_session ,
                                                      upload_url ,
                                                      present_assets ,
                                                      file_temp ,
                                                      properties ,
                                                      no_data )

if __name__ == "__main__":
    main ( sys.argv[1:] )