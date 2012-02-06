# -*- coding: utf-8 -*-
"""Recipe genwebupc"""

import urllib2
import os


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

    def install(self):
        """Installer"""
        # XXX Implement recipe functionality here

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        options = self.options
        directory = self.buildout['buildout'].get('directory')

        DEFAULT_CONFIG_DIR = '%s/config' % directory

        configdir = options.get('configdir', DEFAULT_CONFIG_DIR)
        if not os.path.exists(configdir):
            os.mkdir(configdir)
            raise AssertionError('Configuration placeholder %s did not exist (now it does) and therefore no configuration found.' % configdir)

        configservertype = options.get('configservertype', 'file')

        zeoconfig = [c for c in options.get('zeoconfig', None).splitlines() if c]
        if not zeoconfig:
            raise AssertionError('No ZEO servers to configure')

        zeonames = []
        zeoportsmap = {}
        for zeomap in zeoconfig:
            zeomap = zeomap.split(' ')
            if len(zeomap) != 2:
                raise AssertionError('Config for zeoconfig options have an odd number of items. It must have two, the zeo name and its port.')
            zeonames.append(zeomap[0])
            zeoportsmap[zeomap[0]] = zeomap[1]

        deploytype = options.get('deploytype', 'zeo')

        if deploytype == 'zeo':

            # Make sure that an active zeo part exist and have the name specified in zeomap
            zeo_recipes = (
                'plone.recipe.zeoserver',
                'plone.recipe.zope2zeoserver',
                )
            parts = self.buildout['buildout']['parts']
            part_names = parts.split()
            activezeo = False
            for part_name in part_names:
                part = self.buildout[part_name]
                if part.get('recipe') in zeo_recipes:
                    activezeo = True
                    if part_name not in zeonames:
                        raise AssertionError('No zeoname specified for buildout part name: %s' % (part_name))
                    if not part.get('zeo-conf-additional'):
                        raise AssertionError('No additional mountpoint config for part name: %s' % (part_name))
            if not activezeo:
                raise AssertionError('No active zeo recipe part name.')

            for zeoname in zeonames:

                if configservertype == 'http':
                    configserver = options.get('configserver', 'localhost')
                    try:
                        instancies = urllib2.urlopen(('http://' + configserver + '/instancies/' + zeoname), None)
                    except:
                        raise AssertionError('Error accessing URL: %s' % ('http://' + configserver + '/instancies/' + zeoname))
                else:
                    try:
                        instancies = open(configdir + '/' + zeoname, "r")
                    except:
                        raise AssertionError('No zeoname config file found in %s for %s' % (configdir, zeoname))

                configZeoFile = open(configdir + '/' + 'instancies-' + zeoname + ".conf", "w")

                for instance in instancies.readlines():
                    instance = instance.replace('\n', '')
                    # Now we write the ZEO config
                    configZeoFile.write("<blobstorage " + instance + ">\n")
                    configZeoFile.write("  blob-dir /var/plone/genwebupcZEO/produccio/var/blobs/" + instance + "\n")
                    configZeoFile.write("  <filestorage " + instance + ">\n")
                    configZeoFile.write("    path " + directory + "/var/filestorage/Data_" + instance + ".fs\n")
                    configZeoFile.write("  </filestorage>\n")
                    configZeoFile.write("</blobstorage>\n")

                configZeoFile.close()
                instancies.close()

        if deploytype == 'zope':

            # Make sure that an active zope part exist and have an additional config
            zope_recipes = (
                'plone.recipe.zope2instance',
                )
            parts = self.buildout['buildout']['parts']
            part_names = parts.split()
            activezeo = False
            for part_name in part_names:
                part = self.buildout[part_name]
                if part.get('recipe') in zope_recipes:
                    activezeo = True
                    if not part.get('zope-conf-additional'):
                        raise AssertionError('No additional mountpoint config for part name: %s' % (part_name))
            if not activezeo:
                raise AssertionError('No active zeo recipe part name.')

            localhost = options.get('localhost', 'localhost')

            # zeonames zeos = ['zeo1', 'zeo2', 'zeo3', 'zeo4', 'zeo5', 'zeo7', 'zeo8', 'zeo9', 'zeo10', 'zeo11', ]
            # ports = {'zeo1':8001, 'zeo2':8002, 'zeo3':8003, 'zeo4':8004, 'zeo5':8005, 'zeo6':8006, 'zeo7':8007, 'zeo8':8008, 'zeo9':8009, 'zeo10':8010, 'zeo11':8011, 'zeo12':8012,}
            # configserver = 'mebsuta.upc.es'

            # Download or adquire from filesystem the Zope instances map for this frontend
            if configservertype == 'http':
                configserver = options.get('configserver', 'localhost')
                try:
                    configFE = urllib2.urlopen(('http://' + configserver + '/config/' + localhost), None)
                except:
                    raise AssertionError('Error accessing URL: %s' % ('http://' + configserver + '/config/ ' + localhost))
            else:
                try:
                    configFE = open(configdir + '/' + localhost, "r")
                except:
                    raise AssertionError('No zeoname config file found in %s for %s' % (configdir, localhost))

            # assignacions = {'zeo1':[], 'zeo2':[], 'zeo3':[], 'zeo4':[], 'zeo5':[], 'zeo6':[], 'zeo7':[], 'zeo8':[], 'zeo9':[], 'zeo10':[], 'zeo11':[], 'zeo12':[],}
            # servers = {'zeo1':"", 'zeo2':"", 'zeo3':"", 'zeo4':"", 'zeo5':"", 'zeo6':"", 'zeo7':"", 'zeo8':"", 'zeo9':"", 'zeo10':"", 'zeo11':"", 'zeo12':"",}
            # for assignacio in configFE:
            #     assignacio = assignacio.split()
            #     assignacions[assignacio[0]].append(assignacio[1])
            #     servers[assignacio[0]] = assignacio[3]

            zopemaps = {}
            servers = {}

            for line in configFE:
                zeo, fe, port, be = line.split()
                zopemap = zopemaps.setdefault(zeo, [])
                zopemap.append(fe)

                if zeo not in servers:
                    servers[zeo] = be

            for zeoname in zeonames:
                # Download or adquire from filesystem the ZODB mount point map
                # for this frontend and the corresponding backend
                for zope in zopemaps[zeoname]:
                    if configservertype == 'http':
                        configserver = options.get('configserver', 'localhost')
                        try:
                            instancies = urllib2.urlopen(('http://' + configserver + '/instancies/' + zeoname), None)
                        except:
                            raise AssertionError('Error accessing URL: %s' % ('http://' + configserver + '/instancies/' + zeoname))
                    else:
                        try:
                            instancies = open(configdir + '/' + zeoname, "r")
                        except:
                            raise AssertionError('No zeoname config file found in %s for %s' % (configdir, zeoname))

                    zopeConfigFile = open(configdir + '/' + zope + '-mountpoints.conf', "w")
                    self.writeZopeConfig(directory, zopeConfigFile, instancies, zeoname, servers[zeoname], zeoportsmap)
                    zopeConfigFile.close()
                    instancies.close()

        return tuple()

    def writeZopeConfig(self, directory, zopeConfigFile, instancies, zeoname, server, zeoportsmap):
        for instance in instancies:
            instance = instance.strip('\n')
            zopeConfigFile.write("<zodb_db " + instance + ">\n")
            zopeConfigFile.write("  cache-size 5000\n")
            zopeConfigFile.write("  <zeoclient>\n")
            zopeConfigFile.write("     blob-dir " + directory + "/var/blobs/" + instance + "\n")
            zopeConfigFile.write("     shared-blob-dir off\n")
            zopeConfigFile.write("     server " + server + ":" + str(zeoportsmap[zeoname]) + "\n")
            zopeConfigFile.write("     min-disconnect-poll 1\n")
            zopeConfigFile.write("     storage " + instance + "\n")
            zopeConfigFile.write("     name " + instance + "\n")
            zopeConfigFile.write("     cache-size 20MB\n")
            zopeConfigFile.write("  </zeoclient>\n")
            zopeConfigFile.write("  mount-point /" + instance + "\n")
            zopeConfigFile.write("</zodb_db>\n")

    def update(self):
        """Updater"""
        pass
