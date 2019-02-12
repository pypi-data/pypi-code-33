
import os
import re
import twentyc.tmpl


class Install(object):


    def __init__(self, fax):
        self._fax = fax

    def _package_group(self, grp, dst_dir):
        """
        """
        processed=[]

        # perform every call in case paths have changed
        # TODO replace with config render
        # pre codec.load will fix any special char issues
        tr_list = [
            ('$SRC_DIR$', self.os_path_transform(self._fax.src_dir)),
            ('$BUILD_DIR$', self.os_path_transform(self._fax.build_dirname)),
            ('$DEPLOY_DIR$', self.os_path_transform(self._fax.deploy_dir)),
            ('$CONFIGURATION_NAME$', self._fax.configuration_name)
        ]

        additional = []
        typ = grp.get('type', 'copy')

        if typ == 'tmpl':
            Tmpl = twentyc.tmpl.get_engine(self._fax.tmpl_engine)
            # FIXME - tmpl bug - tmpl = Tmpl(out_dir=self.release_dir, env=self.state.tree())

            for tmpl_dir in self._fax.tmpl_path(grp.get('dir')):
                tmpl = Tmpl(tmpl_dir=tmpl_dir, out_dir=dst_dir, env=self._fax.state.tree())
                # FIXME tmpl bug, render_walk doesn't return list
                #processed.extend(tmpl.render_walk(skip=grp.get('skip', None)))
                rendered = tmpl.render_walk(skip=grp.get('skip', None))
                self._fax.debug_msg("tmpl rendered %s" % str(rendered))

            return

        if typ != 'copy':
            raise ValueError("invalid typ %s" % (typ))

        if 'optfiles' in grp:
            additional = self.transform(tr_list, [self.os_path_transform(f) for f in grp['optfiles']])
            additional = [src for src in additional if os.path.exists(src)]

        if 'files' in grp:
            files = self.transform(tr_list, [self.os_path_transform(f) for f in grp['files']])
            if 'pattern' in grp:
                mangle = re.compile(self.transform(tr_list, self.os_path_transform(grp['pattern'])))
                for src in files + additional:
                    dst = self.resolve_dst(dst_dir, mangle.sub(grp['replace'], src))
                    if not os.path.exists(os.path.dirname(dst)):
                        os.makedirs(os.path.dirname(dst))
                    self._fax.cp(src, dst)
            else:
                for src in files + additional:
                    dst = self.resolve_dst(dst_dir, src)
                    if not os.path.exists(os.path.dirname(dst)):
                        os.makedirs(os.path.dirname(dst))
                    self._fax.cp(src, dst)

        if 'dir' in grp:
            src = self.transform(tr_list, grp['dir'])
            if 'pattern' in grp:
                self._fax.debug_msg("setting mangle to " + grp['pattern'])
                mangle = re.compile(self.transform(tr_list, grp['pattern']))
            else:
                mangle = None

            for root, dirs, files in os.walk(src):
                self._fax.debug_msg("got root dir %s" % (root))

                for name in dirs:
                    dir = os.path.join(root, name)
                    if mangle:
                        dir = mangle.sub(grp['replace'], dir)
                    dir = os.path.join(dst_dir, dir)
                    self._fax.mkdir(dir)

                for name in files:
                    srcfile = os.path.join(root, name)
                    if mangle:
                        dstfile = os.path.join(
                            dst_dir, mangle.sub(grp['replace'], srcfile))
                    else:
                        dstfile = os.path.join(dst_dir, srcfile)

                    self._fax.debug_msg("dstfile is " + dstfile)
                    self._fax.cp(srcfile, dstfile)

    def os_path_transform(self, s, sep=os.path.sep):
        """ transforms any os path into unix style """
        if sep == '/':
            return s
        else:
            return s.replace(sep, '/')

    def transform(self, tr_list, files):
        """
        replaces $tokens$ with values
        will be replaced with config rendering
        """
        singular = False
        if not isinstance(files, list) and not isinstance(files, tuple):
            singular = True
            files = [files]

        for _find, _replace in tr_list:
            files = [opt.replace(_find, _replace) for opt in files]

        if singular:
            return files[0]
        else:
            return files



    def resolve_dir(self, dir):
        """
        gets the actual dir for source files
        relative to FIXME unless absolute path (starts with '/')
// templates relative to define_dir unless abs or ./ ../
        templates would be relative to cwd if ./ ../

        """
        pass

    def resolve_dst(self, dst_dir, src):
        """
        finds the destination based on source
        if source is an absolute path, and there's no pattern, it copies the file to base dst_dir
        """
        if os.path.isabs(src):
            return os.path.join(dst_dir, os.path.basename(src))
        return os.path.join(dst_dir, src)




