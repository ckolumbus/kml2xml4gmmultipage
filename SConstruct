env = Environment(tools=['default', 'packaging'])

env.InstallAs(target = 'bin/kml2xml4gmmultipage', source = 'src/kml2xml4gmmultipage.py')

env.Package( NAME           = 'kml2xml4gmmultipage',
             VERSION        = '0.2',
             PACKAGEVERSION = 0,
             PACKAGETYPE    = 'targz',
             LICENSE        = 'gpl',
             SUMMARY        = 'Converter from Google Earth kml to xml for the Joomla Google Maps Multipage component',
             source         = [ './doc/README', './doc/gpl.txt', './bin/kml2xml4gmmultipage' ]
        )
