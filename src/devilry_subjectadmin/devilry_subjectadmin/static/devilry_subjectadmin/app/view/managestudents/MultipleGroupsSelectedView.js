/**
 * A panel that displays information about multple groups.
 */
Ext.define('devilry_subjectadmin.view.managestudents.MultipleGroupsSelectedView' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.multiplegroupsview',
    cls: 'devilry_subjectadmin_multiplegroupsview',
    requires: [
        'devilry_subjectadmin.view.managestudents.ManageExaminersOnMultiple',
        'devilry_subjectadmin.view.managestudents.ManageTagsOnMultiple',
        'devilry_subjectadmin.view.managestudents.MergeGroups',
        'devilry_subjectadmin.view.managestudents.MultiDangerousActions'
    ],

    /**
     * @cfg {string} topMessage (required)
     */

    /**
     * @cfg {string} multiselectHowto (required)
     */

    /**
     * @cfg {int} [period_id]
     */

    initComponent: function() {
        var defaultmargin = '15 0 0 0';

        Ext.apply(this, {
            layout: 'border',
            border: false,
            frame: false,
            items: [{
                region: 'center',
                xtype: 'container',
                padding: 20,
                layout: 'anchor',
                itemId: 'scrollableBodyContainer',
                autoScroll: true,
                items: [{
                    xtype: 'alertmessage',
                    cls: 'top_infobox',
                    type: 'info',
                    message: [this.topMessage, this.multiselectHowto].join(' ')
                }, {
                    xtype: 'manageexaminersonmultiple',
                    period_id: this.period_id
                }, {
                    xtype: 'mergegroups',
                    margin: defaultmargin
                }, {
                    xtype: 'managetagsonmultiple',
                    margin: defaultmargin,
                }, {
                    xtype: 'multigroupdangerous',
                    margin: defaultmargin,
                    padding: '0 0 20 0'
                }]
            }, {
                xtype: 'selectedgroupssummarygrid',
                region: 'south',
                height: 300,
                minHeight: 100, // Prevent it from beeing completely hidden (this should show at least most of the first selected item)
                //collapsible: true,
                title: gettext('Selected groups (click group to deselect it)'),
                frame: false,
                border: '1 0 0 0',

                // Only resize at the top
                resizable: true,
                resizeHandles: 'n'
            }]
        });
        this.callParent(arguments);
    }
});
