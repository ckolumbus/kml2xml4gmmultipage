env = Environment(tools=['default', 'packaging'])

#env.Install('/usr/local/bin/', 'kml2xml4gmmultipage')
env.InstallAs(target = './bin/kml2xml4gmmultipage', source = './src/kml2xml4gmmultipage.py')




env.Package( NAME           = 'kml2xml4gmmultipage',
             VERSION        = '0.2',
             PACKAGEVERSION = 0,
             PACKAGETYPE    = 'targz',
             LICENSE        = 'gpl',
             SUMMARY        = 'Converter from Google Earth kml to xml for the Joomla Google Maps Multipage component',
        )

