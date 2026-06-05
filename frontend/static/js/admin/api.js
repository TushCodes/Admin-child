/**
 * @file Provides a shared admin API client with timeout, login, and JSON handling.
 */
(function () {
  var DEFAULT_TIMEOUT = 15000;

  function _fetchJson(url, options) {
    options = options || {};
    var signal = options.signal || null;
    var timeout = typeof options.timeout === 'number' ? options.timeout : DEFAULT_TIMEOUT;

    var controller = new AbortController();
    var timer = setTimeout(function () { controller.abort(); }, timeout);
    if (signal) {
      // Prefer provided signal; if it aborts, we still clear timeout.
      signal.addEventListener('abort', function () { controller.abort(); });
    }

    var fetchOptions = Object.assign({}, options, { signal: controller.signal });
    return fetch(url, fetchOptions).then(function (response) {
      clearTimeout(timer);

      if (response.status === 401) {
        var authError = new Error('Authentication required');
        authError.status = 401;
        throw authError;
      }

      return response.text().then(function (responseText) {
        var contentType = response.headers.get('content-type') || '';
        var isHtml = contentType.indexOf('text/html') !== -1 || /^\s*</.test(responseText || '');
        if (isHtml) {
          var loginUrl = '/admin/login';
          var redirectedToLogin =
            (response.url && response.url.indexOf(loginUrl) !== -1) ||
            (
              responseText &&
              responseText.indexOf('name="username"') !== -1 &&
              responseText.indexOf('name="password"') !== -1
            );
          if (redirectedToLogin) {
            return {
              success: false,
              status: 401,
              message: 'Authentication required',
              body: null
            };
          }

          var htmlError = new Error('Invalid JSON response');
          htmlError.response = response;
          throw htmlError;
        }

        try {
          var json = responseText ? JSON.parse(responseText) : {};
          if (!response.ok) {
            var requestError = new Error(
              json && (json.error || json.message)
                ? (json.error || json.message)
                : 'Request failed'
            );
            requestError.response = response;
            requestError.body = json;
            throw requestError;
          }
          return json;
        } catch (error) {
          if (error instanceof SyntaxError) {
            var jsonError = new Error('Invalid JSON response');
            jsonError.response = response;
            throw jsonError;
          }
          throw error;
        }
      });
    }).catch(function (error) {
      if (error.name === 'AbortError') {
        var timeoutError = new Error('Request timed out');
        timeoutError.name = 'TimeoutError';
        throw timeoutError;
      }
      throw error;
    });
  }

  function fetchList(listUrl, params) {
    var queryString = params ? ('?' + new URLSearchParams(params).toString()) : '';
    return _fetchJson(listUrl + queryString, { method: 'GET' }).catch(function (error) {
      return {
        success: false,
        status: error.status || 500,
        message: error.message || 'Request failed',
        body: error.body || null
      };
    });
  }

  function saveRows(saveUrl, payload) {
    return _fetchJson(saveUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).catch(function (error) {
      return {
        success: false,
        status: error.status || 500,
        message: error.message || 'Request failed',
        body: error.body || null
      };
    });
  }

  function deletePod(rowId) {
    var url = '/admin/consignments/' + encodeURIComponent(rowId) + '/pod';
    return _fetchJson(url, {
      method: 'DELETE',
      headers: { 'Accept': 'application/json' }
    }).catch(function (error) {
      return {
        success: false,
        status: error.status || 500,
        message: error.message || 'Request failed',
        body: error.body || null
      };
    });
  }

  window.adminAPI = {
    fetchList: fetchList,
    saveRows: saveRows,
    deletePod: deletePod
  };
})();
