/**
 * @file Keeps unsaved admin table changes.
 */
(function () {
  /** Makes a fresh Set for row ids. */
  function createSet() { return new Set(); }

  var state = {
    deletedIds: createSet(),
    modifiedRowIds: createSet(),
    locallyAddedRows: [],
    newRowIdCounter: 0,

    // Rows marked for delete before Save is clicked.
    addDeleted: function (id) { if (id) this.deletedIds.add(Number(id)); },
    clearDeleted: function () { this.deletedIds.clear(); },

    // Rows edited locally before Save is clicked.
    addModified: function (id) { if (id) this.modifiedRowIds.add(Number(id)); },
    clearModified: function () { this.modifiedRowIds.clear(); },

    // New rows use temporary negative ids until saved.
    pushLocalRow: function (row) { this.locallyAddedRows.push(row); },
    removeLocalRowById: function (id) {
      var rowIndex = this.locallyAddedRows.findIndex(function (row) { return row.id === id; });
      if (rowIndex !== -1) this.locallyAddedRows.splice(rowIndex, 1);
    },
    nextLocalId: function () { this.newRowIdCounter += 1; return -(this.newRowIdCounter); },

    // Reset local table changes after save/reload.
    resetAfterSave: function () {
      this.clearDeleted();
      this.clearModified();
      this.locallyAddedRows = [];
      this.newRowIdCounter = 0;
    }
  };

  window.adminState = state;
})();
