from lylwm_ui import settings

if __name__ == '__main__':
    if settings.PROD and settings.SERVER == 'cherrypy':
        import cherrypy
        from lylwm_ui.app import app

        cherrypy.tree.graft(app.wsgi_app, '/')
        cherrypy.config.update({
            'global': {
                'environment': 'production',
                'server.thread_pool': 4,
                'server.socket_port': settings.PORT,
                'server.socet_host': '0.0.0.0'
            }
        })

        logger.info('starting server...')
        cherrypy.engine.start()
        cherrypy.engine.block()
    else:
        from lylwm_ui import app
        logger.info('starting Flask app...')
        app.run()