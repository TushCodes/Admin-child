/**
 * @file Runs the interactive admin consignment table, edits, POD preview, and save flow.
 */
document.addEventListener("DOMContentLoaded", function () {
    var tableBody = document.getElementById("sheet-body");
    var saveButton = document.getElementById("save-btn");
    var addRowButton = document.getElementById("add-row-btn");
    var editModal = new bootstrap.Modal(document.getElementById("editConsignmentModal"));
    var modalSaveButton = document.getElementById("modal-save-btn");
    var modalPodFile = document.getElementById("modal-pod-file");
    var modalPodPreview = document.getElementById("modal-pod-preview-container");
    var modalPodRemoveButton = document.getElementById("modal-pod-remove");
    var modalPodView = document.getElementById("modal-pod-view");
    var podViewerModalElement = document.getElementById("podViewerModal");
    var podViewerModal = podViewerModalElement ? new bootstrap.Modal(podViewerModalElement) : null;
    var podViewerContent = document.getElementById("pod-viewer-content");
    var searchInput = document.getElementById("search-input");
    var perPageSelect = document.getElementById("per-page-select");
    var clearFiltersButton = document.getElementById("clear-filters-btn");
    var prevPageButton = document.getElementById("prev-page-btn");
    var nextPageButton = document.getElementById("next-page-btn");
    var paginationContainer = document.getElementById("page-numbers-container");

    if (!tableBody || !saveButton || !addRowButton) {
        return;
    }

    var saveUrl = tableBody.dataset.saveUrl || "";
    var listUrl = tableBody.dataset.listUrl || "";
    var currentEditingRow = null;
    var isCreatingRow = false;
    var searchTimeout;
    var currentPage = 1;
    var currentPerPage = perPageSelect ? (parseInt(perPageSelect.value, 10) || 10) : 10;
    var currentSearch = "";
    var currentSortBy = "id";
    var currentSortOrder = "asc";
    var totalRows = 0;
    var totalPages = 1;
    var stagedPodUpload = null;
    var statusTimeoutId = null;

    function showStatus(message, type) {
        var statusElement = document.getElementById("status-msg");
        if (!statusElement) {
            return;
        }
        statusElement.innerHTML = message;
        statusElement.className = "alert alert-" + type + " shadow-sm border-0";
        statusElement.classList.remove("d-none");
        statusElement.scrollIntoView({ behavior: "smooth", block: "center" });
        // Auto-dismiss status messages after 10 seconds
        try {
            if (statusTimeoutId) {
                clearTimeout(statusTimeoutId);
            }
            statusTimeoutId = setTimeout(function () {
                try {
                    statusElement.classList.add('d-none');
                } catch (error) {}
            }, 10000);
        } catch (error) {}
    }

    function escapeHtml(text) {
        return String(text == null ? "" : text)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#39;");
    }

    function populateModal(row) {
        var consignmentInput = document.getElementById("modal-consignment-number");
        consignmentInput.value = row.consignment_number || "";
        // Ensure the input is editable (some scripts may toggle readOnly)
        try {
            consignmentInput.readOnly = false;
        } catch (error) {
            // ignore
        }
        consignmentInput.focus();
        document.getElementById("modal-status").value = row.status || "";
        document.getElementById("modal-pickup-address").value = row.pickup_address || "";
        document.getElementById("modal-pickup-pincode").value = row.pickup_pincode || "";
        document.getElementById("modal-pickup-tag").value = row.pickup_tag || "";
        document.getElementById("modal-pickup-date").value = row.pickup_date || "";
        document.getElementById("modal-drop-address").value = row.drop_address || "";
        document.getElementById("modal-drop-pincode").value = row.drop_pincode || "";
        document.getElementById("modal-drop-tag").value = row.drop_tag || "";
        document.getElementById("modal-drop-date").value = row.drop_date || "";
        // POD preview and controls
        try {
            if (row.pod_image) {
                modalPodPreview.innerHTML = '<span class="text-success">POD uploaded.</span>';
                modalPodView.style.display = '';
                modalPodView.dataset.id = row.id || '';
                modalPodView.dataset.pod = encodeURIComponent(row.pod_image || '');
            } else if (row.pod_file_name) {
                modalPodPreview.innerHTML = '<span class="text-info">POD ready: ' + escapeHtml(row.pod_file_name) + '</span>';
                modalPodView.style.display = '';
                modalPodView.dataset.id = row.id || '';
                modalPodView.dataset.pod = encodeURIComponent(row.pod_file_data || '');
            } else {
                modalPodPreview.innerHTML = '<em class="text-muted">No POD uploaded.</em>';
                modalPodView.style.display = 'none';
                modalPodView.dataset.id = '';
                modalPodView.dataset.pod = '';
            }
        } catch (error) {
            // ignore if modal controls missing
        }
    }

    function clearModal() {
        stagedPodUpload = null;
        if (modalPodFile) {
            modalPodFile.value = "";
        }
        populateModal({
            consignment_number: "",
            status: "",
            pickup_address: "",
            pickup_pincode: "",
            pickup_tag: "",
            pickup_date: "",
            drop_address: "",
            drop_pincode: "",
            drop_tag: "",
            drop_date: "",
            eta: "",
            pod_image: null,
            pod_file_name: null,
            pod_file_type: null,
            pod_file_data: null
        });
    }

    function buildRowData(source, fallbackId) {
        var data = source || {};
        return {
            id: data.id || fallbackId || null,
            consignment_number: data.consignment_number || "",
            status: data.status || "",
            pickup_address: data.pickup_address || "",
            pickup_pincode: data.pickup_pincode || "",
            pickup_tag: data.pickup_tag || "",
            pickup_date: data.pickup_date || "",
            drop_address: data.drop_address || "",
            drop_pincode: data.drop_pincode || "",
            drop_tag: data.drop_tag || "",
            drop_date: data.drop_date || "",
            eta: data.eta || "",
            pod_image: data.pod_image || null,
            pod_file_name: data.pod_file_name || null,
            pod_file_type: data.pod_file_type || null,
            pod_file_data: data.pod_file_data || null
        };
    }

    function getRowDataFromElement(rowElement) {
        try {
            return buildRowData(JSON.parse(rowElement.dataset.row || "{}"), rowElement.dataset.id ? Number(rowElement.dataset.id) : null);
        } catch (error) {
            return buildRowData({}, rowElement.dataset.id ? Number(rowElement.dataset.id) : null);
        }
    }

    function addRow(row, isLocal) {
        var source = buildRowData(row || {});
        var rowElement = document.createElement("tr");
        rowElement.dataset.id = source.id || "";
        rowElement.dataset.consignmentNumber = source.consignment_number || "";
        rowElement.dataset.row = JSON.stringify(source);
        rowElement.dataset.isLocal = isLocal ? "true" : "false";

        var consignmentNumberText = escapeHtml(source.consignment_number || "");
        var status = escapeHtml(source.status || "");
        var pickupTag = escapeHtml(source.pickup_tag || "");
        var dropPincodeText = escapeHtml(source.drop_pincode || "");
        var pickupDate = escapeHtml(source.pickup_date || "");
        var dropEtaText = escapeHtml(source.drop_date || source.eta || "");

        var rowCssClass = isLocal ? 'table-info' : '';

        var podCellMarkup = "<span class=\"text-muted small\">—</span>";
        if (source.pod_image) {
            podCellMarkup = '<button type="button" class="btn btn-sm btn-outline-secondary view-pod">View</button>';
        } else if (source.pod_file_name) {
            podCellMarkup = '<button type="button" class="btn btn-sm btn-outline-secondary view-pod">View</button>';
        }

        rowElement.innerHTML =
            "<td>" + consignmentNumberText + "</td>" +
            "<td>" + status + "</td>" +
            "<td>" + pickupTag + "</td>" +
            "<td>" + dropPincodeText + "</td>" +
            "<td>" + pickupDate + "</td>" +
            "<td>" + dropEtaText + "</td>" +
            "<td class=\"text-center\">" + podCellMarkup + "</td>" +
            "<td class=\"text-center\"><button type=\"button\" class=\"btn btn-sm btn-outline-primary edit-row\" title=\"Edit\"><i class=\"fa fa-pencil\"></i></button></td>" +
            "<td class=\"text-center\"><button type=\"button\" class=\"btn btn-sm btn-outline-danger delete-row\" title=\"Delete\"><i class=\"fa fa-times\"></i></button></td>";

        if (rowCssClass) {
            rowElement.className = rowCssClass;
        }

        var editButton = rowElement.querySelector(".edit-row");
        if (editButton) {
            editButton.addEventListener("click", function () {
                isCreatingRow = false;
                currentEditingRow = rowElement;
                populateModal(getRowDataFromElement(rowElement));
                editModal.show();
            });
        }

        var deleteButton = rowElement.querySelector(".delete-row");
        if (deleteButton) {
            deleteButton.addEventListener("click", function () {
                var existingId = rowElement.dataset.id ? Number(rowElement.dataset.id) : null;
                if (existingId && existingId > 0) {
                    adminState.addDeleted(existingId);
                }
                // Remove from local tracking
                adminState.removeLocalRowById(existingId);
                rowElement.remove();
            });
        }

        tableBody.appendChild(rowElement);

        // attach view-pod listener if present
        var viewButton = rowElement.querySelector('.view-pod');
        if (viewButton) {
            viewButton.addEventListener('click', function () {
                openPodViewer(getRowDataFromElement(rowElement));
            });
        }
    }

    function updateRowFromModal(rowElement, source) {
        var consignmentNumber = document.getElementById("modal-consignment-number").value.trim();
        var status = document.getElementById("modal-status").value.trim();
        var pickupPincode = document.getElementById("modal-pickup-pincode").value.trim();
        var dropPincode = document.getElementById("modal-drop-pincode").value.trim();

        if (!consignmentNumber) {
            showStatus("Consignment number cannot be empty.", "danger");
            return false;
        }

        if (!adminValidation.validatePincode(pickupPincode)) {
            showStatus("Pickup Pincode must be a valid 6-digit number or empty.", "danger");
            return false;
        }
        if (!adminValidation.validatePincode(dropPincode)) {
            showStatus("Drop Pincode must be a valid 6-digit number or empty.", "danger");
            return false;
        }

        source.consignment_number = consignmentNumber;
        source.status = status;
        source.pickup_address = document.getElementById("modal-pickup-address").value.trim();
        source.pickup_pincode = adminValidation.normalizePincode(pickupPincode);
        source.pickup_tag = document.getElementById("modal-pickup-tag").value.trim();
        source.pickup_date = document.getElementById("modal-pickup-date").value.trim();
        source.drop_address = document.getElementById("modal-drop-address").value.trim();
        source.drop_pincode = adminValidation.normalizePincode(dropPincode);
        source.drop_tag = document.getElementById("modal-drop-tag").value.trim();
        source.drop_date = document.getElementById("modal-drop-date").value.trim();
        source.pod_file_name = stagedPodUpload ? stagedPodUpload.name : (source.pod_file_name || null);
        source.pod_file_type = stagedPodUpload ? stagedPodUpload.type : (source.pod_file_type || null);
        source.pod_file_data = stagedPodUpload ? stagedPodUpload.dataUrl : (source.pod_file_data || null);

        if (rowElement) {
            rowElement.cells[0].textContent = source.consignment_number || "";
            rowElement.dataset.consignmentNumber = source.consignment_number || "";
            rowElement.cells[1].textContent = source.status || "";
            rowElement.dataset.row = JSON.stringify(source);
            rowElement.cells[2].textContent = source.pickup_tag || "";
            rowElement.cells[3].textContent = source.drop_pincode || "";
            rowElement.cells[4].textContent = source.pickup_date || "";
            rowElement.cells[5].textContent = source.drop_date || source.eta || "";

            // update POD cell (cell index 6)
            try {
                var podCell = rowElement.cells[6];
                if (podCell) {
                    if (source.pod_image || source.pod_file_data) {
                        podCell.innerHTML = '<button type="button" class="btn btn-sm btn-outline-secondary view-pod">View</button>';
                        var viewButton = podCell.querySelector('.view-pod');
                        if (viewButton) {
                            viewButton.addEventListener('click', function () {
                                openPodViewer(getRowDataFromElement(rowElement));
                            });
                        }
                    } else {
                        podCell.innerHTML = '<span class="text-muted small">—</span>';
                    }
                }
            } catch (error) {}

            // Track modification
            var rowId = rowElement.dataset.id ? Number(rowElement.dataset.id) : null;
            if (rowId && rowId > 0) {
                adminState.addModified(rowId);
            }
        }

        return true;
    }

    function collectRows() {
        var rows = [];
        var tableRows = document.querySelectorAll("#sheet-body tr");

        tableRows.forEach(function (rowElement) {
            var rowData = getRowDataFromElement(rowElement);
            if (rowData.consignment_number && rowData.consignment_number.trim()) {
                rows.push(rowData);
            }
        });

        return rows;
    }

    async function saveSheet() {
        if (!saveUrl) {
            showStatus("Save endpoint is missing.", "danger");
            return;
        }

        var rawRows = collectRows();
        // Include staged local rows that may not be present in DOM (user hasn't navigated to last page)
        try {
            var staged = (adminState && adminState.locallyAddedRows) ? adminState.locallyAddedRows : [];
            staged.forEach(function (stagedRow) {
                var exists = rawRows.some(function (row) { return row.id === stagedRow.id; });
                if (!exists) rawRows.push(stagedRow);
            });
        } catch (error) {}
        if (!rawRows.length && adminState.deletedIds.size === 0) {
            showStatus("No changes to save.", "warning");
            return;
        }

        try {
            saveButton.disabled = true;
            var originalButtonText = saveButton.textContent;
            saveButton.textContent = "Saving...";
            showStatus('<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Saving rows to database...', "info");

            // Delegate network call to adminAPI
            var data = await adminAPI.saveRows(saveUrl, {
                rows: rawRows,
                deleted_ids: Array.from(adminState.deletedIds)
            });

            // Handle structured per-row validation errors from the server
            if (data && Array.isArray(data.errors) && data.errors.length) {
                // Clear any previous row error markers
                document.querySelectorAll('#sheet-body tr .row-error').forEach(function (element) { element.remove(); });
                var rowElements = Array.from(document.querySelectorAll('#sheet-body tr'));
                var firstRowElement = null;
                data.errors.forEach(function (rowError) {
                    var rowIndex = rowError.index || 0;
                    var message = rowError.message || 'Invalid value';
                    var rowElement = rowElements[rowIndex];
                    if (!rowElement) return;
                    firstRowElement = firstRowElement || rowElement;
                    rowElement.classList.add('table-danger');
                    // insert or update an inline error element
                    var existing = rowElement.querySelector('.row-error');
                    if (existing) {
                        existing.textContent = message;
                    } else {
                        var cell = document.createElement('td');
                        cell.colSpan = rowElement.cells.length;
                        cell.className = 'row-error text-danger small';
                        cell.textContent = message;
                        var errorRowElement = document.createElement('tr');
                        errorRowElement.className = 'row-error-row';
                        errorRowElement.appendChild(cell);
                        rowElement.parentNode.insertBefore(errorRowElement, rowElement.nextSibling);
                    }
                });

                if (firstRowElement) {
                    firstRowElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }

                throw new Error('Validation errors. Please fix highlighted rows.');
            }

            if (!data || !data.success) {
                throw new Error((data && data.message) || "Save failed.");
            }

            showStatus("<strong>Saved successfully.</strong> Your internal database has been updated.", "success");
            adminState.resetAfterSave();
            setTimeout(function () {
                // Prefer server-provided total (after commit) to compute the
                // page that will contain newly inserted rows. Fall back to
                // an estimate using the locally tracked counts.
                try {
                    var totalAfter = (data && typeof data.total === 'number')
                        ? data.total
                        : (totalRows + (adminState.locallyAddedRows ? adminState.locallyAddedRows.length : 0) - (data.deleted_count || 0));
                    var lastPage = Math.max(1, Math.ceil(totalAfter / currentPerPage));
                    loadPage(lastPage, currentSearch, currentPerPage, currentSortBy, currentSortOrder);
                } catch (error) {
                    loadPage(1, currentSearch, currentPerPage, currentSortBy, currentSortOrder);
                }
            }, 1200);
        } catch (error) {
            showStatus("<strong>Save failed.</strong> " + escapeHtml(error.message || "Please check the row values and try again."), "danger");
        } finally {
            saveButton.disabled = false;
            saveButton.textContent = "Save All";
        }
    }

    async function loadPage(page, search, perPage, sortBy, sortOrder) {
        if (!listUrl) {
            showStatus("List endpoint is missing.", "danger");
            return;
        }

        try {
            var params = {
                page: page,
                per_page: perPage,
                search: search,
                sort_by: sortBy,
                sort_order: sortOrder
            };

            showLoadingSpinner(true);

            // clear any inline validation rows before loading new data
            try {
                document.querySelectorAll('#sheet-body .row-error').forEach(function (element) { element.remove(); });
                document.querySelectorAll('.row-error-row').forEach(function (element) { element.remove(); });
                document.querySelectorAll('#sheet-body tr.table-danger').forEach(function (rowElement) { rowElement.classList.remove('table-danger'); });
            } catch (error) {}

            var data = await adminAPI.fetchList(listUrl, params);
            if (!data || !data.success) {
                // If authentication is required, redirect to login so the user can re-authenticate
                try {
                    if (data && data.status === 401) {
                        window.location = '/admin/login';
                        return;
                    }
                } catch (error) {}
                throw new Error((data && data.error) || "Failed to load data.");
            }

            // Clear existing rows
            tableBody.innerHTML = "";

            // Add fetched rows
            data.rows.forEach(function (row) {
                addRow(row, false);
            });

            // Include locally staged rows in totals (but only render them when showing the last page)
            var stagedCount = (adminState && adminState.locallyAddedRows) ? adminState.locallyAddedRows.length : 0;

            // Update pagination info: totalRows includes staged rows
            totalRows = (typeof data.total === "number" ? data.total : 0) + stagedCount;
            totalPages = Math.max(1, Math.ceil(totalRows / perPage));
            currentPage = page;
            currentPerPage = perPage;
            currentSearch = search;
            currentSortBy = sortBy;
            currentSortOrder = sortOrder;

            // If this is the last page (after accounting for staged rows), append staged rows to the DOM.
            // Render staged rows without the local highlight (pass isLocal = false).
            if (stagedCount > 0 && page === totalPages) {
                try {
                    adminState.locallyAddedRows.forEach(function (row) {
                        // show staged rows on last page but without 'table-info' highlight
                        addRow(row, false);
                    });
                } catch (error) {
                    // ignore DOM append errors
                }
            }

            updatePaginationUI();
            updateSortHeaders();

        } catch (error) {
            showStatus("<strong>Failed to load data.</strong> " + escapeHtml(error.message || "Please try again."), "danger");
        } finally {
            showLoadingSpinner(false);
        }
    }

    function updatePaginationUI() {
        var showingStart = (currentPage - 1) * currentPerPage + 1;
        var showingEnd = Math.min(currentPage * currentPerPage, totalRows);

        document.getElementById("showing-start").textContent = totalRows > 0 ? showingStart : 0;
        document.getElementById("showing-end").textContent = showingEnd;
        document.getElementById("total-count").textContent = totalRows;

        prevPageButton.disabled = currentPage <= 1;
        nextPageButton.disabled = currentPage >= totalPages;

        // Generate page numbers
        paginationContainer.innerHTML = "";
        var startPage = Math.max(1, currentPage - 2);
        var endPage = Math.min(totalPages, currentPage + 2);

        if (startPage > 1) {
            var firstPageButton = document.createElement("button");
            firstPageButton.type = "button";
            firstPageButton.className = "btn btn-outline-secondary btn-sm page-number";
            firstPageButton.textContent = "1";
            firstPageButton.addEventListener("click", function () {
                loadPage(1, currentSearch, currentPerPage, currentSortBy, currentSortOrder);
            });
            paginationContainer.appendChild(firstPageButton);

            if (startPage > 2) {
                var ellipsis = document.createElement("span");
                ellipsis.className = "page-number";
                ellipsis.textContent = "...";
                paginationContainer.appendChild(ellipsis);
            }
        }

        for (var pageNumber = startPage; pageNumber <= endPage; pageNumber++) {
            var pageButton = document.createElement("button");
            pageButton.type = "button";
            pageButton.className = "btn btn-sm page-number";
            if (pageNumber === currentPage) {
                pageButton.className += " btn-primary";
                pageButton.disabled = true;
            } else {
                pageButton.className += " btn-outline-secondary";
            }
            pageButton.textContent = pageNumber;
            pageButton.addEventListener("click", function (page) {
                return function () {
                    loadPage(page, currentSearch, currentPerPage, currentSortBy, currentSortOrder);
                };
            }(pageNumber));
            paginationContainer.appendChild(pageButton);
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                var trailingEllipsis = document.createElement("span");
                trailingEllipsis.className = "page-number";
                trailingEllipsis.textContent = "...";
                paginationContainer.appendChild(trailingEllipsis);
            }

            var lastPageButton = document.createElement("button");
            lastPageButton.type = "button";
            lastPageButton.className = "btn btn-outline-secondary btn-sm page-number";
            lastPageButton.textContent = totalPages;
            lastPageButton.addEventListener("click", function () {
                loadPage(totalPages, currentSearch, currentPerPage, currentSortBy, currentSortOrder);
            });
            paginationContainer.appendChild(lastPageButton);
        }
    }

    function updateSortHeaders() {
        var headers = document.querySelectorAll(".sort-header");
        headers.forEach(function (header) {
            var icon = header.querySelector(".sort-icon i");
            var column = header.dataset.sortColumn;
            if (column === currentSortBy) {
                icon.className = currentSortOrder === "asc" ? "fa fa-sort-up" : "fa fa-sort-down";
                header.querySelector(".sort-icon").classList.add("active");
            } else {
                icon.className = "fa fa-sort";
                header.querySelector(".sort-icon").classList.remove("active");
            }
        });
    }

    function showLoadingSpinner(show) {
        var spinner = document.getElementById("loading-spinner");
        if (show) {
            spinner.classList.remove("d-none");
        } else {
            spinner.classList.add("d-none");
        }
    }

    // Event Listeners
    modalSaveButton.addEventListener("click", function () {
        if (isCreatingRow) {
            var newId = adminState.nextLocalId();
            var newSource = buildRowData({}, newId);
            if (updateRowFromModal(null, newSource)) {
                // Stage row in admin state but do not add to DOM yet
                adminState.pushLocalRow(newSource);

                // Clear any staged POD upload buffer from the modal
                stagedPodUpload = null;
                try { if (modalPodFile) modalPodFile.value = ""; } catch (error) {}

                // Update totals and pagination UI, but do not navigate or re-load pages
                totalRows = (typeof totalRows === "number" ? totalRows : 0) + 1;
                totalPages = Math.max(1, Math.ceil(totalRows / currentPerPage));
                updatePaginationUI();

                showStatus("Row staged locally. Click 'Save All' to persist changes.", "info");

                // Close modal and reset local editing state
                editModal.hide();
                currentEditingRow = null;
                isCreatingRow = false;
            }
            return;
        }

        if (currentEditingRow) {
            var source = getRowDataFromElement(currentEditingRow);
            if (updateRowFromModal(currentEditingRow, source)) {
                editModal.hide();
                currentEditingRow = null;
                isCreatingRow = false;
            }
        }
    });

    addRowButton.addEventListener("click", function () {
        isCreatingRow = true;
        currentEditingRow = null;
        clearModal();
        editModal.show();
    });

    document.getElementById("editConsignmentModal").addEventListener("hidden.bs.modal", function () {
        currentEditingRow = null;
        isCreatingRow = false;
        clearModal();
    });

    // POD chooser: stage selected image silently until the modal Save button is clicked.
    if (modalPodFile) {
        modalPodFile.addEventListener('change', function () {
            var file = modalPodFile.files && modalPodFile.files[0];
            if (!file) {
                stagedPodUpload = null;
                return;
            }

            if (!/^image\//.test(file.type || '')) {
                modalPodFile.value = null;
                stagedPodUpload = null;
                return;
            }

            var reader = new FileReader();
            reader.onload = function () {
                stagedPodUpload = {
                    name: file.name,
                    type: file.type,
                    dataUrl: String(reader.result || ""),
                    file: file,
                };
            };
            reader.readAsDataURL(file);
        });
    }

    if (modalPodRemoveButton) {
        modalPodRemoveButton.addEventListener('click', async function () {
            if (!currentEditingRow) {
                modalPodPreview.innerHTML = '<em class="text-muted">No POD uploaded.</em>';
                modalPodView.style.display = 'none';
                return;
            }

            // Read the current row data to determine whether the POD exists on the server
            var rowData = getRowDataFromElement(currentEditingRow) || {};

            // If the row only has a staged upload (client-side) but no persisted `pod_image`,
            // clear the staged preview locally instead of calling the DELETE endpoint.
            if (!rowData.pod_image && (rowData.pod_file_data || rowData.pod_file_name)) {
                // Clear staged upload
                stagedPodUpload = null;
                try {
                    rowData.pod_file_data = null;
                    rowData.pod_file_name = null;
                    rowData.pod_file_type = null;
                    currentEditingRow.dataset.row = JSON.stringify(rowData);
                } catch (error) {}
                modalPodFile.value = '';
                modalPodPreview.innerHTML = '<em class="text-muted">No POD uploaded.</em>';
                modalPodView.style.display = 'none';
                showStatus('Cleared staged POD (not yet saved).', 'info');
                return;
            }

            var rowId = Number(currentEditingRow.dataset.id) || null;
            if (!rowId || rowId <= 0) {
                // No persisted row id — nothing to delete server-side
                modalPodPreview.innerHTML = '<em class="text-muted">No POD uploaded.</em>';
                modalPodView.style.display = 'none';
                return;
            }

            if (!confirm('Remove POD for this consignment? This will delete the file.')) return;

            try {
                var data = await adminAPI.deletePod(rowId);
                if (!data || !data.success) throw new Error((data && data.message) || 'Delete failed');

                // Update UI
                try {
                    var rowElement = currentEditingRow;
                    var rowData = getRowDataFromElement(rowElement);
                    rowData.pod_image = null;
                    rowData.pod_file_name = null;
                    rowData.pod_file_type = null;
                    rowData.pod_file_data = null;
                    rowElement.dataset.row = JSON.stringify(rowData);
                    var podCell = rowElement.cells[6];
                    if (podCell) podCell.innerHTML = '<span class="text-muted small">—</span>';
                    modalPodPreview.innerHTML = '<em class="text-muted">No POD uploaded.</em>';
                    modalPodView.style.display = 'none';
                    try { modalPodView.dataset.id = ''; modalPodView.dataset.pod = ''; } catch (error) {}
                    showStatus('POD removed.', 'success');
                } catch (error) {}

            } catch (rowError) {
                showStatus('Failed to remove POD: ' + (rowError.message || ''), 'danger');
            }
        });
    }

    // Open POD viewer when modal's 'View POD' button clicked
    if (modalPodView) {
        modalPodView.addEventListener('click', function () {
            openPodViewer(currentEditingRow ? getRowDataFromElement(currentEditingRow) : null);
        });
    }

    function openPodViewer(rowData) {
        if (!podViewerModal || !podViewerContent) return;
        rowData = rowData || {};
        var podPath = rowData.pod_image || rowData.pod_file_data || '';
        if (!podPath) {
            podViewerContent.innerHTML = '<div class="text-center text-muted">No POD available.</div>';
            podViewerModal.show();
            return;
        }

        var imageSource = rowData.pod_image ? '/admin/consignments/' + rowData.id + '/pod' : podPath;
        podViewerContent.innerHTML = '<img src="' + imageSource + '" style="max-width:100%;max-height:75vh;height:auto;display:block;margin:0 auto;" />';
        podViewerModal.show();
    }

    saveButton.addEventListener("click", saveSheet);

    // Search with debouncing
    searchInput.addEventListener("input", function () {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(function () {
            loadPage(1, searchInput.value.trim(), currentPerPage, currentSortBy, currentSortOrder);
        }, 500);
    });

    // Per-page selector
    perPageSelect.addEventListener("change", function () {
        currentPerPage = parseInt(perPageSelect.value);
        loadPage(1, currentSearch, currentPerPage, currentSortBy, currentSortOrder);
    });

    // Clear filters
    clearFiltersButton.addEventListener("click", function () {
        searchInput.value = "";
        perPageSelect.value = "10";
        currentPerPage = 10;
        currentSearch = "";
        loadPage(1, "", 10, "id", "asc");
    });

    // Pagination buttons
    prevPageButton.addEventListener("click", function () {
        if (currentPage > 1) {
            loadPage(currentPage - 1, currentSearch, currentPerPage, currentSortBy, currentSortOrder);
        }
    });

    nextPageButton.addEventListener("click", function () {
        if (currentPage < totalPages) {
            loadPage(currentPage + 1, currentSearch, currentPerPage, currentSortBy, currentSortOrder);
        }
    });

    // Sort headers
    var sortHeaders = document.querySelectorAll(".sort-header");
    sortHeaders.forEach(function (header) {
        header.addEventListener("click", function () {
            var column = header.dataset.sortColumn;
            var newOrder = "asc";
            if (currentSortBy === column && currentSortOrder === "asc") {
                newOrder = "desc";
            }
            loadPage(1, currentSearch, currentPerPage, column, newOrder);
        });
    });

    // Initial load: prefer server-rendered `data-existing-rows` when present
    (function initialLoad() {
        var existingJson = tableBody.dataset.existingRows || "";
        if (existingJson) {
            try {
                var existingRows = JSON.parse(existingJson || "[]") || [];
                if (existingRows.length) {
                    tableBody.innerHTML = "";
                    // Respect rows-per-page on initial render: only render the first page
                    var displayRows = existingRows.slice(0, currentPerPage);
                    displayRows.forEach(function (row) { addRow(row, false); });
                    totalRows = existingRows.length;
                    totalPages = Math.max(1, Math.ceil(totalRows / currentPerPage));
                    currentPage = 1;
                    // Ensure the per-page select reflects the active value
                    try { if (perPageSelect) perPageSelect.value = String(currentPerPage); } catch (error) {}
                    updatePaginationUI();
                    updateSortHeaders();
                    return;
                }
            } catch (error) {
                // Fall through to API load on parse error
            }
        }

        // Fallback to paginated API load
        loadPage(1, "", currentPerPage, currentSortBy, currentSortOrder);
    })();

    // Auto-hide any server-rendered alerts on page load after 10s, unless they set data-autodismiss="false"
    try {
        setTimeout(function () {
            var alerts = document.querySelectorAll('.alert');
            alerts.forEach(function (a) {
                try {
                    if (a.dataset && a.dataset.autodismiss === 'false') return;
                    a.classList.add('d-none');
                } catch (error) {}
            });
        }, 10000);
    } catch (error) {}
});

