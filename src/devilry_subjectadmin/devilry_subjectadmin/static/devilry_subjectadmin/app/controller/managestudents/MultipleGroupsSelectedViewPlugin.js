/**
 * Plugin for {@link devilry_subjectadmin.controller.managestudents.Overview} that
 * adds the ability to show information about and edit a multiple groups when
 * they are selected.
 */
Ext.define('devilry_subjectadmin.controller.managestudents.MultipleGroupsSelectedViewPlugin', {
    extend: 'Ext.app.Controller',

    views: [
        'managestudents.MultipleGroupsSelectedView',
        'managestudents.ChooseExaminersWindow',
        'managestudents.SelectedGroupsSummaryGrid'
    ],

    requires: [
        'devilry_extjsextras.AlertMessage',
        'devilry_subjectadmin.utils.Array',
        'Ext.window.Window',
        'Ext.tip.ToolTip'
    ],

    stores: ['SelectedGroups'],

    refs: [{
        ref: 'setExaminersPanel',
        selector: '#setExaminersWindow chooseexaminerspanel'
    }, {
        ref: 'addExaminersPanel',
        selector: '#addExaminersWindow chooseexaminerspanel'
    }],

    init: function() {
        this.application.addListener({
            scope: this,
            managestudentsMultipleGroupsSelected: this._onMultipleGroupsSelected
        });
        this.control({
            'viewport multiplegroupsview': {
                render: this._onRender
            },
            'viewport multiplegroupsview selectedgroupssummarygrid': {
                beforeselect: this._onSelectGroupInSummaryGrid
            },

            // setExaminers
            'viewport multiplegroupsview #setExaminersButton': {
                click: this._onSetExaminers
            },
            '#setExaminersWindow chooseexaminerspanel': {
                addUser: this._onExaminerSetAdd,
                removeUsers: this._onExaminerSetRemove
            },

            // addExaminers
            'viewport multiplegroupsview #addExaminersButton': {
                click: this._onAddExaminers
            },
            '#addExaminersWindow chooseexaminerspanel': {
                addUser: this._onExaminerAddPanelAdd
            },

            // clearExaminers
            'viewport multiplegroupsview #clearExaminersButton': {
                click: this._onClearExaminers
            },
        });
    },

    _onMultipleGroupsSelected: function(manageStudentsController, groupRecords) {
        this.groupRecords = groupRecords;
        this.manageStudentsController = manageStudentsController;
        this.manageStudentsController.setBody({
            xtype: 'multiplegroupsview',
            multiselectHowto: this.manageStudentsController.getMultiSelectHowto(),
            topMessage: this._createTopMessage()
        });

        this._populateSelectedGroupsStore();
    },

    _populateSelectedGroupsStore: function() {
        var store = this.getSelectedGroupsStore();
        //Ext.Array.each(this.groupRecords, function(groupRecord, index) {
            //console.log(groupRecord, 'loaded');
            //store.add(groupRecord);
        //}, this);
        store.removeAll();
        store.loadData(this.groupRecords);
    },

    _onRender: function() {
        //console.log('render MultipleGroupsSelectedView');
    },

    _createTopMessage: function() {
        var tpl = Ext.create('Ext.XTemplate', gettext('{numselected}/{total} {groupunit_plural} selected.'));
        return tpl.apply({
            numselected: this.groupRecords.length,
            total: this.manageStudentsController.getTotalGroupsCount(),
            groupunit_plural: this.manageStudentsController.getTranslatedGroupUnit(true)
        });
    },

    _onSetExaminers: function() {
        Ext.widget('chooseexaminerswindow', {
            title: gettext('Set examiners'),
            itemId: 'setExaminersWindow',
            panelConfig: {
                includeRemove: true,
                sourceStore: this.manageStudentsController.getRelatedExaminersRoStore()
            }
        }).show();
    },

    _onAddExaminers: function() {
        Ext.widget('chooseexaminerswindow', {
            title: gettext('Add examiners'),
            itemId: 'addExaminersWindow',
            panelConfig: {
                sourceStore: this.manageStudentsController.getRelatedExaminersRoStore()
            }
        }).show();
    },

    _onClearExaminers: function() {
        Ext.MessageBox.show({
            title: gettext('Configm clear examiners'),
            msg: gettext('Do you want to remove all examiners from the selected groups? Their existing feedback will not be removed, only their permission to give feedback on the groups.'),
            buttons: Ext.MessageBox.YESNO,
            icon: Ext.MessageBox.QUESTION,
            scope: this,
            fn: function(buttonid) {
                if(buttonid == 'yes') {
                    this._clearExaminers();
                }
            }
        });
    },

    _clearExaminers: function() {
        Ext.Array.each(this.groupRecords, function(groupRecord) {
            groupRecord.set('examiners', []);
        }, this);
        this.manageStudentsController.notifyMultipleGroupsChange();
    },

    _syncExaminers: function(userStore, doNotDeleteUsers) {
        for(var index=0; index<this.groupRecords.length; index++)  {
            var groupRecord = this.groupRecords[index];
            var examiners = [];
            var currentExaminers = groupRecord.get('examiners');
            devilry_subjectadmin.utils.Array.mergeIntoArray({
                destinationArray: currentExaminers,
                sourceArray: userStore.data.items,
                isEqual: function(examiner, userRecord) {
                    return examiner.user.id == userRecord.get('id');
                },
                onMatch: function(examiner) {
                    examiners.push(examiner);
                },
                onNoMatch: function(examiner) {
                    if(doNotDeleteUsers) {
                        examiners.push(examiner);
                    }
                },
                onAdd: function(userRecord) {
                    examiners.push({
                        user: {id: userRecord.get('id')}
                    });
                }
            });
            groupRecord.set('examiners', examiners);
        }
    },

    _onExaminerSetAdd: function(addedUserRecord) {
        var userStore = this.getSetExaminersPanel().store;
        this._syncExaminers(userStore);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
                this.getSetExaminersPanel().afterItemAddedSuccessfully(addedUserRecord);
            }
        });
    },

    _onExaminerSetRemove: function(removedUserRecords) {
        var userStore = this.getSetExaminersPanel().store;
        this._syncExaminers(userStore);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
                this.getSetExaminersPanel().afterItemsRemovedSuccessfully(removedUserRecords);
            }
        });
    },

    _onExaminerAddPanelAdd: function(addedUserRecord) {
        var userStore = this.getAddExaminersPanel().store;
        this._syncExaminers(userStore, true);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
                this.getAddExaminersPanel().afterItemAddedSuccessfully(addedUserRecord);
            }
        });
    },

    _onSelectGroupInSummaryGrid: function(rowmodel, selectedGroupRecord) {
        // NOTE: This selectedGroupRecord is not from the same proxy as the records in the
        //       "regular" list, so their internal IDs do not match. Therefore,
        //       we use getGroupRecordById() to get the correct receord.
        var groupId = selectedGroupRecord.get('id');
        var groupRecord = this.manageStudentsController.getGroupRecordById(groupId);
        // NOTE: We defer deselecting to ensure that we return ``false`` before
        //       deselecting. If we deselect before returning, the grid will be gone
        //       when we return, and that causes an exception.
        Ext.defer(function() {
            this.manageStudentsController.deselectGroupRecords([groupRecord]);
        }, 10, this);
        return false;
    }
});
