from das.server import DartAnalysisServer


DartAnalysisServer.api_version = [1, 6, 2]


@DartAnalysisServer.register_domain('server')
class ServerDomain:
    """The server domain contains API’s related to the execution of the
    server.
    """

    def get_version(self, *, callback=None, errback=None):
        """Return the version number of the analysis server.

        Callback arguments:

        :param version: The version number of the analysis server.
        :type version: str
        """
        method = 'server.getVersion'
        params = {}
        self.server.request(method, params, callback=callback, errback=errback)

    def shutdown(self, *, callback=None, errback=None):
        """Cleanly shutdown the analysis server. Requests that are received
        after this request will not be processed. Requests that were received
        before this request, but for which a response has not yet been sent,
        will not be responded to. No further responses or notifications will
        be sent after the response to this request has been sent.
        """
        method = 'server.shutdown'
        params = {}
        self.server.request(method, params, callback=callback, errback=errback)

    def set_subscriptions(self, subscriptions, *, callback=None, errback=None):
        """Subscribe for services. All previous subscriptions are replaced by
        the given set of services.

        It is an error if any of the elements in the list are not valid
        services. If there is an error, then the current subscriptions will
        remain unchanged.

        :param subscriptions: A list of the services being subscribed to.
        :type subscriptions: [ServerService]
        """
        method = 'server.setSubscriptions'
        params = {'subscriptions': subscriptions}
        self.server.request(method, params, callback=callback, errback=errback)

    def on_connected(self, *, callback):
        """Reports that the server is running. This notification is issued
        once after the server has started running but before any requests are
        processed to let the client know that it started correctly.

        It is not possible to subscribe to or unsubscribe from this
        notification.

        Callback arguments:

        :param version: The version number of the analysis server.
        :type version: str
        """
        event = 'server.connected'
        self.server.notification(event, callback=callback)

    def on_error(self, *, callback):
        """Reports that an unexpected error has occurred while executing the
        server. This notification is not used for problems with specific
        requests (which are returned as part of the response) but is used for
        exceptions that occur while performing other tasks, such as analysis
        or preparing notifications.

        It is not possible to subscribe to or unsubscribe from this
        notification.

        Callback arguments:

        :param is_fatal: True if the error is a fatal error, meaning that the
            server will shutdown automatically after sending this
            notification.
        :type is_fatal: bool

        :param message: The error message indicating what kind of error was
            encountered.
        :type message: str

        :param stack_trace: The stack trace associated with the generation of
            the error, used for debugging the server.
        :type stack_trace: str
        """
        event = 'server.error'
        self.server.notification(event, callback=callback)

    def on_status(self, *, callback):
        """Reports the current status of the server. Parameters are omitted if
        there has been no change in the status represented by that parameter.

        This notification is not subscribed to by default. Clients can
        subscribe by including the value "STATUS" in the list of services
        passed in a server.setSubscriptions request.

        Callback arguments:

        :param analysis: The current status of analysis, including whether
            analysis is being performed and if so what is being analyzed.
        :type analysis: AnalysisStatus

        :param pub: The current status of pub execution, indicating whether we
            are currently running pub.
        :type pub: PubStatus
        """
        event = 'server.status'
        self.server.notification(event, callback=callback)


@DartAnalysisServer.register_domain('analysis')
class AnalysisDomain:
    """The analysis domain contains API’s related to the analysis of
    files.
    """

    def get_errors(self, file, *, callback=None, errback=None):
        """Return the errors associated with the given file. If the errors for
        the given file have not yet been computed, or the most recently
        computed errors for the given file are out of date, then the response
        for this request will be delayed until they have been computed. If
        some or all of the errors for the file cannot be computed, then the
        subset of the errors that can be computed will be returned and the
        response will contain an error to indicate why the errors could not be
        computed. If the content of the file changes after this request was
        received but before a response could be sent, then an error of type
        CONTENT_MODIFIED will be generated.

        This request is intended to be used by clients that cannot
        asynchronously apply updated error information. Clients that can apply
        error information as it becomes available should use the information
        provided by the 'analysis.errors' notification.

        If a request is made for a file which does not exist, or which is not
        currently subject to analysis (e.g. because it is not associated with
        any analysis root specified to analysis.setAnalysisRoots), an error of
        type GET_ERRORS_INVALID_FILE will be generated.

        :param file: The file for which errors are being requested.
        :type file: FilePath

        Callback arguments:

        :param errors: The errors associated with the file.
        :type errors: [AnalysisError]
        """
        method = 'analysis.getErrors'
        params = {'file': file}
        self.server.request(method, params, callback=callback, errback=errback)

    def get_hover(self, file, offset, *, callback=None, errback=None):
        """Return the hover information associate with the given location. If
        some or all of the hover information is not available at the time this
        request is processed the information will be omitted from the
        response.

        :param file: The file in which hover information is being requested.
        :type file: FilePath

        :param offset: The offset for which hover information is being
            requested.
        :type offset: int

        Callback arguments:

        :param hovers: The hover information associated with the location. The
            list will be empty if no information could be determined for the
            location. The list can contain multiple items if the file is being
            analyzed in multiple contexts in conflicting ways (such as a part
            that is included in multiple libraries).
        :type hovers: [HoverInformation]
        """
        method = 'analysis.getHover'
        params = {'file': file, 'offset': offset}
        self.server.request(method, params, callback=callback, errback=errback)

    def get_library_dependencies(self, *, callback=None, errback=None):
        """Return library dependency information for use in client-side
        indexing and package URI resolution.

        Callback arguments:

        :param libraries: A list of the paths of library elements referenced
            by files in existing analysis roots.
        :type libraries: [FilePath]

        :param package_map: A mapping from context source roots to package
            maps which map package names to source directories for use in
            client-side package URI resolution.
        :type package_map: {str: {str: [FilePath]}}
        """
        method = 'analysis.getLibraryDependencies'
        params = {}
        self.server.request(method, params, callback=callback, errback=errback)

    def get_navigation(self, file, offset, length, *, callback=None,
                       errback=None):
        """Return the navigation information associated with the given region
        of the given file. If the navigation information for the given file
        has not yet been computed, or the most recently computed navigation
        information for the given file is out of date, then the response for
        this request will be delayed until it has been computed. If the
        content of the file changes after this request was received but before
        a response could be sent, then an error of type CONTENT_MODIFIED will
        be generated.

        If a navigation region overlaps (but extends either before or after)
        the given region of the file it will be included in the result. This
        means that it is theoretically possible to get the same navigation
        region in response to multiple requests. Clients can avoid this by
        always choosing a region that starts at the beginning of a line and
        ends at the end of a (possibly different) line in the file.

        :param file: The file in which navigation information is being
            requested.
        :type file: FilePath

        :param offset: The offset of the region for which navigation
            information is being requested.
        :type offset: int

        :param length: The length of the region for which navigation
            information is being requested.
        :type length: int

        Callback arguments:

        :param files: A list of the paths of files that are referenced by the
            navigation targets.
        :type files: [FilePath]

        :param targets: A list of the navigation targets that are referenced
            by the navigation regions.
        :type targets: [NavigationTarget]

        :param regions: A list of the navigation regions within the requested
            region of the file.
        :type regions: [NavigationRegion]
        """
        method = 'analysis.getNavigation'
        params = {'length': length, 'file': file, 'offset': offset}
        self.server.request(method, params, callback=callback, errback=errback)

    def reanalyze(self, roots, *, callback=None, errback=None):
        """Force the re-analysis of everything contained in the specified
        analysis roots. This will cause all previously computed analysis
        results to be discarded and recomputed, and will cause all subscribed
        notifications to be re-sent.

        If no analysis roots are provided, then all current analysis roots
        will be re-analyzed. If an empty list of analysis roots is provided,
        then nothing will be re-analyzed. If the list contains one or more
        paths that are not currently analysis roots, then an error of type
        INVALID_ANALYSIS_ROOT will be generated.

        :param roots: A list of the analysis roots that are to be re-analyzed.
        :type roots: [FilePath]
        """
        method = 'analysis.reanalyze'
        params = {'roots': roots}
        self.server.request(method, params, callback=callback, errback=errback)

    def set_analysis_roots(self, included, excluded, package_roots, *,
                           callback=None, errback=None):
        """Sets the root paths used to determine which files to analyze. The
        set of files to be analyzed are all of the files in one of the root
        paths that are not either explicitly or implicitly excluded. A file is
        explicitly excluded if it is in one of the excluded paths. A file is
        implicitly excluded if it is in a subdirectory of one of the root
        paths where the name of the subdirectory starts with a period (that
        is, a hidden directory).

        Note that this request determines the set of requested analysis roots.
        The actual set of analysis roots at any given time is the intersection
        of this set with the set of files and directories actually present on
        the filesystem. When the filesystem changes, the actual set of
        analysis roots is automatically updated, but the set of requested
        analysis roots is unchanged. This means that if the client sets an
        analysis root before the root becomes visible to server in the
        filesystem, there is no error; once the server sees the root in the
        filesystem it will start analyzing it. Similarly, server will stop
        analyzing files that are removed from the file system but they will
        remain in the set of requested roots.

        If an included path represents a file, then server will look in the
        directory containing the file for a pubspec.yaml file. If none is
        found, then the parents of the directory will be searched until such a
        file is found or the root of the file system is reached. If such a
        file is found, it will be used to resolve package: URI’s within the
        file.

        :param included: A list of the files and directories that should be
            analyzed.
        :type included: [FilePath]

        :param excluded: A list of the files and directories within the
            included directories that should not be analyzed.
        :type excluded: [FilePath]

        :param package_roots: A mapping from source directories to target
            directories that should override the normal package: URI
            resolution mechanism. The analyzer will behave as though each
            source directory in the map contains a special pubspec.yaml file
            which resolves any package: URI to the corresponding path within
            the target directory. The effect is the same as specifying the
            target directory as a "--package_root" parameter to the Dart VM
            when executing any Dart file inside the source directory. Files in
            any directories that are not overridden by this mapping have their
            package: URI's resolved using the normal pubspec.yaml mechanism.
            If this field is absent, or the empty map is specified, that
            indicates that the normal pubspec.yaml mechanism should always be
            used.
        :type package_roots: {FilePath: FilePath}
        """
        method = 'analysis.setAnalysisRoots'
        params = {'included': included, 'packageRoots': package_roots,
                  'excluded': excluded}
        self.server.request(method, params, callback=callback, errback=errback)

    def set_priority_files(self, files, *, callback=None, errback=None):
        """Set the priority files to the files in the given list. A priority
        file is a file that is given priority when scheduling which analysis
        work to do first. The list typically contains those files that are
        visible to the user and those for which analysis results will have the
        biggest impact on the user experience. The order of the files within
        the list is significant: the first file will be given higher priority
        than the second, the second higher priority than the third, and so on.

        Note that this request determines the set of requested priority files.
        The actual set of priority files is the intersection of the requested
        set of priority files with the set of files currently subject to
        analysis. (See analysis.setSubscriptions for a description of files
        that are subject to analysis.)

        If a requested priority file is a directory it is ignored, but remains
        in the set of requested priority files so that if it later becomes a
        file it can be included in the set of actual priority files.

        :param files: The files that are to be a priority for analysis.
        :type files: [FilePath]
        """
        method = 'analysis.setPriorityFiles'
        params = {'files': files}
        self.server.request(method, params, callback=callback, errback=errback)

    def set_subscriptions(self, subscriptions, *, callback=None, errback=None):
        """Subscribe for services. All previous subscriptions are replaced by
        the current set of subscriptions. If a given service is not included
        as a key in the map then no files will be subscribed to the service,
        exactly as if the service had been included in the map with an
        explicit empty list of files.

        Note that this request determines the set of requested subscriptions.
        The actual set of subscriptions at any given time is the intersection
        of this set with the set of files currently subject to analysis. The
        files currently subject to analysis are the set of files contained
        within an actual analysis root but not excluded, plus all of the files
        transitively reachable from those files via import, export and part
        directives. (See analysis.setAnalysisRoots for an explanation of how
        the actual analysis roots are determined.) When the actual analysis
        roots change, the actual set of subscriptions is automatically
        updated, but the set of requested subscriptions is unchanged.

        If a requested subscription is a directory it is ignored, but remains
        in the set of requested subscriptions so that if it later becomes a
        file it can be included in the set of actual subscriptions.

        It is an error if any of the keys in the map are not valid services.
        If there is an error, then the existing subscriptions will remain
        unchanged.

        :param subscriptions: A table mapping services to a list of the files
            being subscribed to the service.
        :type subscriptions: {AnalysisService: [FilePath]}
        """
        method = 'analysis.setSubscriptions'
        params = {'subscriptions': subscriptions}
        self.server.request(method, params, callback=callback, errback=errback)

    def update_content(self, files, *, callback=None, errback=None):
        """Update the content of one or more files. Files that were previously
        updated but not included in this update remain unchanged. This
        effectively represents an overlay of the filesystem. The files whose
        content is overridden are therefore seen by server as being files with
        the given content, even if the files do not exist on the filesystem or
        if the file path represents the path to a directory on the filesystem.

        :param files: A table mapping the files whose content has changed to a
            description of the content change.
        :type files: {FilePath: (AddContentOverlay | ChangeContentOverlay |
            RemoveContentOverlay)}
        """
        method = 'analysis.updateContent'
        params = {'files': files}
        self.server.request(method, params, callback=callback, errback=errback)

    def update_options(self, options, *, callback=None, errback=None):
        """Update the options controlling analysis based on the given set of
        options. Any options that are not included in the analysis options
        will not be changed. If there are options in the analysis options that
        are not valid, they will be silently ignored.

        :param options: The options that are to be used to control analysis.
        :type options: AnalysisOptions
        """
        method = 'analysis.updateOptions'
        params = {'options': options}
        self.server.request(method, params, callback=callback, errback=errback)

    def on_errors(self, *, callback):
        """Reports the errors associated with a given file. The set of errors
        included in the notification is always a complete list that supersedes
        any previously reported errors.

        It is only possible to unsubscribe from this notification by using the
        command-line flag --no-error-notification.

        Callback arguments:

        :param file: The file containing the errors.
        :type file: FilePath

        :param errors: The errors contained in the file.
        :type errors: [AnalysisError]
        """
        event = 'analysis.errors'
        self.server.notification(event, callback=callback)

    def on_flush_results(self, *, callback):
        """Reports that any analysis results that were previously associated
        with the given files should be considered to be invalid because those
        files are no longer being analyzed, either because the analysis root
        that contained it is no longer being analyzed or because the file no
        longer exists.

        If a file is included in this notification and at some later time a
        notification with results for the file is received, clients should
        assume that the file is once again being analyzed and the information
        should be processed.

        It is not possible to subscribe to or unsubscribe from this
        notification.

        Callback arguments:

        :param files: The files that are no longer being analyzed.
        :type files: [FilePath]
        """
        event = 'analysis.flushResults'
        self.server.notification(event, callback=callback)

    def on_folding(self, *, callback):
        """Reports the folding regions associated with a given file. Folding
        regions can be nested, but will not be overlapping. Nesting occurs
        when a foldable element, such as a method, is nested inside another
        foldable element such as a class.

        This notification is not subscribed to by default. Clients can
        subscribe by including the value "FOLDING" in the list of services
        passed in an analysis.setSubscriptions request.

        Callback arguments:

        :param file: The file containing the folding regions.
        :type file: FilePath

        :param regions: The folding regions contained in the file.
        :type regions: [FoldingRegion]
        """
        event = 'analysis.folding'
        self.server.notification(event, callback=callback)

    def on_highlights(self, *, callback):
        """Reports the highlight regions associated with a given file.

        This notification is not subscribed to by default. Clients can
        subscribe by including the value "HIGHLIGHTS" in the list of services
        passed in an analysis.setSubscriptions request.

        Callback arguments:

        :param file: The file containing the highlight regions.
        :type file: FilePath

        :param regions: The highlight regions contained in the file. Each
            highlight region represents a particular syntactic or semantic
            meaning associated with some range. Note that the highlight
            regions that are returned can overlap other highlight regions if
            there is more than one meaning associated with a particular
            region.
        :type regions: [HighlightRegion]
        """
        event = 'analysis.highlights'
        self.server.notification(event, callback=callback)

    def on_invalidate(self, *, callback):
        """Reports that the navigation information associated with a region of
        a single file has become invalid and should be re-requested.

        This notification is not subscribed to by default. Clients can
        subscribe by including the value "INVALIDATE" in the list of services
        passed in an analysis.setSubscriptions request.

        Callback arguments:

        :param file: The file whose information has been invalidated.
        :type file: FilePath

        :param offset: The offset of the invalidated region.
        :type offset: int

        :param length: The length of the invalidated region.
        :type length: int

        :param delta: The delta to be applied to the offsets in information
            that follows the invalidated region in order to update it so that
            it doesn't need to be re-requested.
        :type delta: int
        """
        event = 'analysis.invalidate'
        self.server.notification(event, callback=callback)

    def on_navigation(self, *, callback):
        """Reports the navigation targets associated with a given file.

        This notification is not subscribed to by default. Clients can
        subscribe by including the value "NAVIGATION" in the list of services
        passed in an analysis.setSubscriptions request.

        Callback arguments:

        :param file: The file containing the navigation regions.
        :type file: FilePath

        :param regions: The navigation regions contained in the file. The
            regions are sorted by their offsets. Each navigation region
            represents a list of targets associated with some range. The lists
            will usually contain a single target, but can contain more in the
            case of a part that is included in multiple libraries or in Dart
            code that is compiled against multiple versions of a package. Note
            that the navigation regions that are returned do not overlap other
            navigation regions.
        :type regions: [NavigationRegion]

        :param targets: The navigation targets referenced in the file. They
            are referenced by NavigationRegion s by their index in this array.
        :type targets: [NavigationTarget]

        :param files: The files containing navigation targets referenced in
            the file. They are referenced by NavigationTarget s by their index
            in this array.
        :type files: [FilePath]
        """
        event = 'analysis.navigation'
        self.server.notification(event, callback=callback)

    def on_occurrences(self, *, callback):
        """Reports the occurrences of references to elements within a single
        file.

        This notification is not subscribed to by default. Clients can
        subscribe by including the value "OCCURRENCES" in the list of services
        passed in an analysis.setSubscriptions request.

        Callback arguments:

        :param file: The file in which the references occur.
        :type file: FilePath

        :param occurrences: The occurrences of references to elements within
            the file.
        :type occurrences: [Occurrences]
        """
        event = 'analysis.occurrences'
        self.server.notification(event, callback=callback)

    def on_outline(self, *, callback):
        """Reports the outline associated with a single file.

        This notification is not subscribed to by default. Clients can
        subscribe by including the value "OUTLINE" in the list of services
        passed in an analysis.setSubscriptions request.

        Callback arguments:

        :param file: The file with which the outline is associated.
        :type file: FilePath

        :param outline: The outline associated with the file.
        :type outline: Outline
        """
        event = 'analysis.outline'
        self.server.notification(event, callback=callback)

    def on_overrides(self, *, callback):
        """Reports the overridding members in a file.

        This notification is not subscribed to by default. Clients can
        subscribe by including the value "OVERRIDES" in the list of services
        passed in an analysis.setSubscriptions request.

        Callback arguments:

        :param file: The file with which the overrides are associated.
        :type file: FilePath

        :param overrides: The overrides associated with the file.
        :type overrides: [Override]
        """
        event = 'analysis.overrides'
        self.server.notification(event, callback=callback)


@DartAnalysisServer.register_domain('completion')
class CompletionDomain:
    """The code completion domain contains commands related to getting
    code completion suggestions.
    """

    def get_suggestions(self, file, offset, *, callback=None, errback=None):
        """Request that completion suggestions for the given offset in the
        given file be returned.

        :param file: The file containing the point at which suggestions are to
            be made.
        :type file: FilePath

        :param offset: The offset within the file at which suggestions are to
            be made.
        :type offset: int

        Callback arguments:

        :param id: The identifier used to associate results with this
            completion request.
        :type id: CompletionId
        """
        method = 'completion.getSuggestions'
        params = {'file': file, 'offset': offset}
        self.server.request(method, params, callback=callback, errback=errback)

    def on_results(self, *, callback):
        """Reports the completion suggestions that should be presented to the
        user. The set of suggestions included in the notification is always a
        complete list that supersedes any previously reported suggestions.

        Callback arguments:

        :param id: The id associated with the completion.
        :type id: CompletionId

        :param replacement_offset: The offset of the start of the text to be
            replaced. This will be different than the offset used to request
            the completion suggestions if there was a portion of an identifier
            before the original offset. In particular, the replacementOffset
            will be the offset of the beginning of said identifier.
        :type replacement_offset: int

        :param replacement_length: The length of the text to be replaced if
            the remainder of the identifier containing the cursor is to be
            replaced when the suggestion is applied (that is, the number of
            characters in the existing identifier).
        :type replacement_length: int

        :param results: The completion suggestions being reported. The
            notification contains all possible completions at the requested
            cursor position, even those that do not match the characters the
            user has already typed. This allows the client to respond to
            further keystrokes from the user without having to make additional
            requests.
        :type results: [CompletionSuggestion]

        :param is_last: True if this is that last set of results that will be
            returned for the indicated completion.
        :type is_last: bool
        """
        event = 'completion.results'
        self.server.notification(event, callback=callback)


@DartAnalysisServer.register_domain('search')
class SearchDomain:
    """The search domain contains commands related to searches that can be
    performed against the code base.
    """

    def find_element_references(self, file, offset, include_potential, *,
                                callback=None, errback=None):
        """Perform a search for references to the element defined or
        referenced at the given offset in the given file.

        An identifier is returned immediately, and individual results will be
        returned via the search.results notification as they become available.

        :param file: The file containing the declaration of or reference to
            the element used to define the search.
        :type file: FilePath

        :param offset: The offset within the file of the declaration of or
            reference to the element.
        :type offset: int

        :param include_potential: True if potential matches are to be included
            in the results.
        :type include_potential: bool

        Callback arguments:

        :param id: The identifier used to associate results with this search
            request. If no element was found at the given location, this field
            will be absent, and no results will be reported via the
            search.results notification.
        :type id: SearchId

        :param element: The element referenced or defined at the given offset
            and whose references will be returned in the search results. If no
            element was found at the given location, this field will be
            absent.
        :type element: Element
        """
        method = 'search.findElementReferences'
        params = {'includePotential': include_potential, 'file': file,
                  'offset': offset}
        self.server.request(method, params, callback=callback, errback=errback)

    def find_member_declarations(self, name, *, callback=None, errback=None):
        """Perform a search for declarations of members whose name is equal to
        the given name.

        An identifier is returned immediately, and individual results will be
        returned via the search.results notification as they become available.

        :param name: The name of the declarations to be found.
        :type name: str

        Callback arguments:

        :param id: The identifier used to associate results with this search
            request.
        :type id: SearchId
        """
        method = 'search.findMemberDeclarations'
        params = {'name': name}
        self.server.request(method, params, callback=callback, errback=errback)

    def find_member_references(self, name, *, callback=None, errback=None):
        """Perform a search for references to members whose name is equal to
        the given name. This search does not check to see that there is a
        member defined with the given name, so it is able to find references
        to undefined members as well.

        An identifier is returned immediately, and individual results will be
        returned via the search.results notification as they become available.

        :param name: The name of the references to be found.
        :type name: str

        Callback arguments:

        :param id: The identifier used to associate results with this search
            request.
        :type id: SearchId
        """
        method = 'search.findMemberReferences'
        params = {'name': name}
        self.server.request(method, params, callback=callback, errback=errback)

    def find_top_level_declarations(self, pattern, *, callback=None,
                                    errback=None):
        """Perform a search for declarations of top-level elements (classes,
        typedefs, getters, setters, functions and fields) whose name matches
        the given pattern.

        An identifier is returned immediately, and individual results will be
        returned via the search.results notification as they become available.

        :param pattern: The regular expression used to match the names of the
            declarations to be found.
        :type pattern: str

        Callback arguments:

        :param id: The identifier used to associate results with this search
            request.
        :type id: SearchId
        """
        method = 'search.findTopLevelDeclarations'
        params = {'pattern': pattern}
        self.server.request(method, params, callback=callback, errback=errback)

    def get_type_hierarchy(self, file, offset, *, callback=None, errback=None):
        """Return the type hierarchy of the class declared or referenced at
        the given location.

        :param file: The file containing the declaration or reference to the
            type for which a hierarchy is being requested.
        :type file: FilePath

        :param offset: The offset of the name of the type within the file.
        :type offset: int

        Callback arguments:

        :param hierarchy_items: A list of the types in the requested
            hierarchy. The first element of the list is the item representing
            the type for which the hierarchy was requested. The index of other
            elements of the list is unspecified, but correspond to the
            integers used to reference supertype and subtype items within the
            items. This field will be absent if the code at the given file and
            offset does not represent a type, or if the file has not been
            sufficiently analyzed to allow a type hierarchy to be produced.
        :type hierarchy_items: [TypeHierarchyItem]
        """
        method = 'search.getTypeHierarchy'
        params = {'file': file, 'offset': offset}
        self.server.request(method, params, callback=callback, errback=errback)

    def on_results(self, *, callback):
        """Reports some or all of the results of performing a requested
        search. Unlike other notifications, this notification contains search
        results that should be added to any previously received search results
        associated with the same search id.

        Callback arguments:

        :param id: The id associated with the search.
        :type id: SearchId

        :param results: The search results being reported.
        :type results: [SearchResult]

        :param is_last: True if this is that last set of results that will be
            returned for the indicated search.
        :type is_last: bool
        """
        event = 'search.results'
        self.server.notification(event, callback=callback)


@DartAnalysisServer.register_domain('edit')
class EditDomain:
    """The edit domain contains commands related to edits that can be
    applied to the code.
    """

    def format(self, file, selection_offset, selection_length, *, callback=None,
               errback=None):
        """Format the contents of a single file. The currently selected region
        of text is passed in so that the selection can be preserved across the
        formatting operation. The updated selection will be as close to
        matching the original as possible, but whitespace at the beginning or
        end of the selected region will be ignored. If preserving selection
        information is not required, zero (0) can be specified for both the
        selection offset and selection length.

        If a request is made for a file which does not exist, or which is not
        currently subject to analysis (e.g. because it is not associated with
        any analysis root specified to analysis.setAnalysisRoots), an error of
        type FORMAT_INVALID_FILE will be generated. If the source contains
        syntax errors, an error of type FORMAT_WITH_ERRORS will be generated.

        :param file: The file containing the code to be formatted.
        :type file: FilePath

        :param selection_offset: The offset of the current selection in the
            file.
        :type selection_offset: int

        :param selection_length: The length of the current selection in the
            file.
        :type selection_length: int

        Callback arguments:

        :param edits: The edit(s) to be applied in order to format the code.
            The list will be empty if the code was already formatted (there
            are no changes).
        :type edits: [SourceEdit]

        :param selection_offset: The offset of the selection after formatting
            the code.
        :type selection_offset: int

        :param selection_length: The length of the selection after formatting
            the code.
        :type selection_length: int
        """
        method = 'edit.format'
        params = {'selectionLength': selection_length, 'file': file,
                  'selectionOffset': selection_offset}
        self.server.request(method, params, callback=callback, errback=errback)

    def get_assists(self, file, offset, length, *, callback=None, errback=None):
        """Return the set of assists that are available at the given location.
        An assist is distinguished from a refactoring primarily by the fact
        that it affects a single file and does not require user input in order
        to be performed.

        :param file: The file containing the code for which assists are being
            requested.
        :type file: FilePath

        :param offset: The offset of the code for which assists are being
            requested.
        :type offset: int

        :param length: The length of the code for which assists are being
            requested.
        :type length: int

        Callback arguments:

        :param assists: The assists that are available at the given location.
        :type assists: [SourceChange]
        """
        method = 'edit.getAssists'
        params = {'length': length, 'file': file, 'offset': offset}
        self.server.request(method, params, callback=callback, errback=errback)

    def get_available_refactorings(self, file, offset, length, *, callback=None,
                                   errback=None):
        """Get a list of the kinds of refactorings that are valid for the
        given selection in the given file.

        :param file: The file containing the code on which the refactoring
            would be based.
        :type file: FilePath

        :param offset: The offset of the code on which the refactoring would
            be based.
        :type offset: int

        :param length: The length of the code on which the refactoring would
            be based.
        :type length: int

        Callback arguments:

        :param kinds: The kinds of refactorings that are valid for the given
            selection.
        :type kinds: [RefactoringKind]
        """
        method = 'edit.getAvailableRefactorings'
        params = {'length': length, 'file': file, 'offset': offset}
        self.server.request(method, params, callback=callback, errback=errback)

    def get_fixes(self, file, offset, *, callback=None, errback=None):
        """Return the set of fixes that are available for the errors at a
        given offset in a given file.

        :param file: The file containing the errors for which fixes are being
            requested.
        :type file: FilePath

        :param offset: The offset used to select the errors for which fixes
            will be returned.
        :type offset: int

        Callback arguments:

        :param fixes: The fixes that are available for the errors at the given
            offset.
        :type fixes: [AnalysisErrorFixes]
        """
        method = 'edit.getFixes'
        params = {'file': file, 'offset': offset}
        self.server.request(method, params, callback=callback, errback=errback)

    def get_refactoring(self, kind, file, offset, length, validate_only,
                        options, *, callback=None, errback=None):
        """Get the changes required to perform a refactoring.

        If another refactoring request is received during the processing of
        this one, an error of type REFACTORING_REQUEST_CANCELLED will be
        generated.

        :param kind: The kind of refactoring to be performed.
        :type kind: RefactoringKind

        :param file: The file containing the code involved in the refactoring.
        :type file: FilePath

        :param offset: The offset of the region involved in the refactoring.
        :type offset: int

        :param length: The length of the region involved in the refactoring.
        :type length: int

        :param validate_only: True if the client is only requesting that the
            values of the options be validated and no change be generated.
        :type validate_only: bool

        :param options: Data used to provide values provided by the user. The
            structure of the data is dependent on the kind of refactoring
            being performed. The data that is expected is documented in the
            section titled Refactorings , labeled as “Options”. This field can
            be omitted if the refactoring does not require any options or if
            the values of those options are not known.
        :type options: RefactoringOptions

        Callback arguments:

        :param initial_problems: The initial status of the refactoring, i.e.
            problems related to the context in which the refactoring is
            requested. The array will be empty if there are no known problems.
        :type initial_problems: [RefactoringProblem]

        :param options_problems: The options validation status, i.e. problems
            in the given options, such as light-weight validation of a new
            name, flags compatibility, etc. The array will be empty if there
            are no known problems.
        :type options_problems: [RefactoringProblem]

        :param final_problems: The final status of the refactoring, i.e.
            problems identified in the result of a full, potentially expensive
            validation and / or change creation. The array will be empty if
            there are no known problems.
        :type final_problems: [RefactoringProblem]

        :param feedback: Data used to provide feedback to the user. The
            structure of the data is dependent on the kind of refactoring
            being created. The data that is returned is documented in the
            section titled Refactorings , labeled as “Feedback”.
        :type feedback: RefactoringFeedback

        :param change: The changes that are to be applied to affect the
            refactoring. This field will be omitted if there are problems that
            prevent a set of changes from being computed, such as having no
            options specified for a refactoring that requires them, or if only
            validation was requested.
        :type change: SourceChange

        :param potential_edits: The ids of source edits that are not known to
            be valid. An edit is not known to be valid if there was
            insufficient type information for the server to be able to
            determine whether or not the code needs to be modified, such as
            when a member is being renamed and there is a reference to a
            member from an unknown type. This field will be omitted if the
            change field is omitted or if there are no potential edits for the
            refactoring.
        :type potential_edits: [str]
        """
        method = 'edit.getRefactoring'
        params = {'options': options, 'file': file, 'offset': offset, 'kind':
                  kind, 'length': length, 'validateOnly': validate_only}
        self.server.request(method, params, callback=callback, errback=errback)

    def sort_members(self, file, *, callback=None, errback=None):
        """Sort all of the directives, unit and class members of the given
        Dart file.

        If a request is made for a file that does not exist, does not belong
        to an analysis root or is not a Dart file, SORT_MEMBERS_INVALID_FILE
        will be generated.

        If the Dart file has scan or parse errors, SORT_MEMBERS_PARSE_ERRORS
        will be generated.

        :param file: The Dart file to sort.
        :type file: FilePath

        Callback arguments:

        :param edit: The file edit that is to be applied to the given file to
            effect the sorting.
        :type edit: SourceFileEdit
        """
        method = 'edit.sortMembers'
        params = {'file': file}
        self.server.request(method, params, callback=callback, errback=errback)


@DartAnalysisServer.register_domain('execution')
class ExecutionDomain:
    """The execution domain contains commands related to providing an
    execution or debugging experience.
    """

    def create_context(self, context_root, *, callback=None, errback=None):
        """Create an execution context for the executable file with the given
        path. The context that is created will persist until
        execution.deleteContext is used to delete it. Clients, therefore, are
        responsible for managing the lifetime of execution contexts.

        :param context_root: The path of the Dart or HTML file that will be
            launched, or the path of the directory containing the file.
        :type context_root: FilePath

        Callback arguments:

        :param id: The identifier used to refer to the execution context that
            was created.
        :type id: ExecutionContextId
        """
        method = 'execution.createContext'
        params = {'contextRoot': context_root}
        self.server.request(method, params, callback=callback, errback=errback)

    def delete_context(self, id, *, callback=None, errback=None):
        """Delete the execution context with the given identifier. The context
        id is no longer valid after this command. The server is allowed to re-
        use ids when they are no longer valid.

        :param id: The identifier of the execution context that is to be
            deleted.
        :type id: ExecutionContextId
        """
        method = 'execution.deleteContext'
        params = {'id': id}
        self.server.request(method, params, callback=callback, errback=errback)

    def map_uri(self, id, file, uri, *, callback=None, errback=None):
        """Map a URI from the execution context to the file that it
        corresponds to, or map a file to the URI that it corresponds to in the
        execution context.

        Exactly one of the file and uri fields must be provided. If both
        fields are provided, then an error of type INVALID_PARAMETER will be
        generated. Similarly, if neither field is provided, then an error of
        type INVALID_PARAMETER will be generated.

        If the file field is provided and the value is not the path of a file
        (either the file does not exist or the path references something other
        than a file), then an error of type INVALID_PARAMETER will be
        generated.

        If the uri field is provided and the value is not a valid URI or if
        the URI references something that is not a file (either a file that
        does not exist or something other than a file), then an error of type
        INVALID_PARAMETER will be generated.

        If the contextRoot used to create the execution context does not
        exist, then an error of type INVALID_EXECUTION_CONTEXT will be
        generated.

        :param id: The identifier of the execution context in which the URI is
            to be mapped.
        :type id: ExecutionContextId

        :param file: The path of the file to be mapped into a URI.
        :type file: FilePath

        :param uri: The URI to be mapped into a file path.
        :type uri: str

        Callback arguments:

        :param file: The file to which the URI was mapped. This field is
            omitted if the uri field was not given in the request.
        :type file: FilePath

        :param uri: The URI to which the file path was mapped. This field is
            omitted if the file field was not given in the request.
        :type uri: str
        """
        method = 'execution.mapUri'
        params = {'uri': uri, 'id': id, 'file': file}
        self.server.request(method, params, callback=callback, errback=errback)

    def set_subscriptions(self, subscriptions, *, callback=None, errback=None):
        """Subscribe for services. All previous subscriptions are replaced by
        the given set of services.

        It is an error if any of the elements in the list are not valid
        services. If there is an error, then the current subscriptions will
        remain unchanged.

        :param subscriptions: A list of the services being subscribed to.
        :type subscriptions: [ExecutionService]
        """
        method = 'execution.setSubscriptions'
        params = {'subscriptions': subscriptions}
        self.server.request(method, params, callback=callback, errback=errback)

    def on_launch_data(self, *, callback):
        """Reports information needed to allow a single file to be launched.

        This notification is not subscribed to by default. Clients can
        subscribe by including the value "LAUNCH_DATA" in the list of services
        passed in an execution.setSubscriptions request.

        Callback arguments:

        :param file: The file for which launch data is being provided. This
            will either be a Dart library or an HTML file.
        :type file: FilePath

        :param kind: The kind of the executable file. This field is omitted if
            the file is not a Dart file.
        :type kind: ExecutableKind

        :param referenced_files: A list of the Dart files that are referenced
            by the file. This field is omitted if the file is not an HTML
            file.
        :type referenced_files: [FilePath]
        """
        event = 'execution.launchData'
        self.server.notification(event, callback=callback)
