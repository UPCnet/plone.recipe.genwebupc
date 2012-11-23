.. contents::

Introduction
============

This recipe is used in production of large Zope/Plone deployments where there are involved several ZEO/Zope servers in spanned across several machines with a complex configuration involved. This complex configuration often involves the one Plone instance-one ZODB mountpoint in large deployments.

With this kind of scenario, you each buildout in each machine needs to be configured with the parameters of the system architecture. The recipe is configured with the recipe parameters AND two external files. This is done on purpose, because this two files contain the common parametrization


Features
========

This recipe maintain this configuration for you, keeping a central configuration point for all the buildouts.

It enables a multi-mountpoint configuration, which is very recommended in large deployments. This guarantees the independence of the data, the backup/restore process and a pluggable and movable architecture.

The recipe allows to setup a complex scenario with several ZEO servers which can be spanned across multiple machines and several Zope clients attacking one of these ZEO servers. It has no limitation on the architecture schema that you desire to have, it will adapt the configuration based on the recipe parameters.

The following examples will explain how to use it based on some common scenarios.


Basic configuration
===================

Let's assume the most basic scenario, a single server with both a ZEO server and a Zope client::

    [buildout]
    parts = genwebconfig zeo1 zc1
    ...

    [genwebconfig]
    recipe = plone.recipe.genwebupc
    deploytype = zope
    configservertype = file
    configdir = ${buildout:directory}/config
    configserver = mebsuta.upc.es
    zeoconfig = zeo1 8001
    localhost = sneridagh.upc.es

    [zeo1]
    recipe = plone.recipe.zeoserver
    zeo-conf-additional = %include ${buildout:directory}/config/instancies-zeo1.conf

    [zc1]
    recipe = plone.recipe.zope2instance
    zope-conf-additional = %include ${buildout:directory}/config/zc1-mountpoints.conf
    ...

This buildout will build the configuration for

Options
=======
