Ext.define('BESDIRAC.TransferAccounting.classes.TransferAccounting', {
    extend : 'Ext.dirac.core.Module',

    requires : [],

    initComponent : function() {
        var me = this;

        me.launcher.title = 'Transfer Accounting';
        me.launcher.maximized = false;
        var oDimensions = GLOBAL.APP.MAIN_VIEW.getViewMainDimensions();
        me.launcher.width = oDimensions[0];
        me.launcher.height = oDimensions[1];
        me.launcher.x = 0;
        me.launcher.y = 0;

        Ext.apply(me, {
                    layout : 'border',
                    bodyBorder : false,
                    defaults : {
                        collapsible : true,
                        split : true
                    }
                });

        me.callParent(arguments);
    },

    buildUI : function() {
        var me = this;

        me.leftPanel = Ext.create('Ext.panel.Panel', {
                    title : 'Selectors',
                    region : "west",
                    layout : 'anchor',
                    floatable : false,
                    margins : '0',
                    width : 250,
                    minWidth : 230,
                    maxWidth : 350,
                    bodyPadding : 5,
                    autoScroll : true,
                    dockedItems : [{
                                xtype : 'toolbar',
                                dock : 'bottom',
                                layout : {
                                    pack : 'center'
                                },
                                items : [{
                                            xtype : 'button',
                                            text : 'Plot',
                                            iconCls : 'dirac-icon-submit',
                                            scope : me,
                                            handler : me.__submit
                                        }, {
                                            xtype : 'button',
                                            text : 'Reset',
                                            iconCls : 'dirac-icon-reset',
                                            scope : me,
                                            handler : me.__reset
                                        }, {
                                            xtype : 'button',
                                            text : 'Refresh',
                                            iconCls : 'dirac-icon-refresh',
                                            scope : me,
                                            handler : me.__refresh
                                        }]
                            }]
                });

        me.rightPanel = Ext.create('Ext.tab.Panel', {
                    header : false,
                    region : 'center',
                    listeners : {
                        scope : me,
                        add : function(tabPanel, addPanel) {
                            tabPanel.setActiveTab(addPanel);
                        },
                        /*tabchange : function(tabPanel, newPanel) {
 *                             var selectors = newPanel.selectors;
 *                                                         me.__setSelectors(selectors);
 *                                                                                             },*/
                    }
                });

                var groupStore = Ext.create('Ext.data.JsonStore', {
                                        fields : ['value', 'text'],
                                        proxy : {
                                                type : 'ajax',
                                                url : GLOBAL.BASE_URL + 'TransferAccounting/getSelectData',
                                                reader : {
                                                        type : 'json',
                                                        root : 'result'
                                                }
                                        }
                                });
        me.cmbGrouping = Ext.create('Ext.form.field.ComboBox', {
                    id : 'Grouping_cmb',
                    name : 'Grouping',
                    fieldLabel : "Group by",
                    queryMode : 'local',
                    labelAlign : 'top',
                    displayField : "text",
                    valueField : "value",
                    anchor : '100%',
                    store :groupStore


                });



        me.cmbPlotName = Ext.create('Ext.form.field.ComboBox', {
                    id : 'PlotName_cmb',
                    name : 'PlotName',
                    fieldLabel : "Plot to generate",
                    queryMode : 'local',
                    labelAlign : 'top',
                    displayField : "plist",
                    valueField : "plist",
                    anchor : '100%',
                    store : new Ext.data.ArrayStore({
                                fields : ['plist'],
                                data : [["DataSizeBin"],["DataTransfered"], ["Quality"], ["Throughput"]]
                            }),
                    listeners : {
                        change : function(field, newValue, oldValue, eOpts) {
                            me.cmbGrouping.clearValue();
                            me.cmbGrouping.getStore().load({});
                            me.cmbUser.getStore().load({});
                            me.cmbSource.getStore().load({});
                            me.cmbDestination.getStore().load({});
                            me.cmbProtocol.getStore().load({});
                            me.cmbFinalStatus.getStore().load({});
                        }
                    }

                });

                var userStore = Ext.create('Ext.data.JsonStore', {
                                        fields : ['value', 'text'],
                                        proxy : {
                                                type : 'ajax',
                                                url : GLOBAL.BASE_URL + 'TransferAccounting/getUser',
                                                reader : {
                                                        type : 'json',
                                                        root : 'result'
                                                }
                                        }
                                });
        me.cmbUser = Ext.create('Ext.dirac.utils.DiracBoxSelect', {
                    id : 'User_cmb',
                    name : 'User',
                    fieldLabel : "User",
                    queryMode : 'local',
                    labelAlign : 'top',
                    displayField : "text",
                    valueField : "value",
                    anchor : '100%',
                    store :userStore
                });

                var sourceStore = Ext.create('Ext.data.JsonStore', {
                                        fields : ['value', 'text'],
                                        proxy : {
                                                type : 'ajax',
                                                url : GLOBAL.BASE_URL + 'TransferAccounting/getSource',
                                                reader : {
                                                        type : 'json',
                                                        root : 'result'
                                                }
                                        }
                                });
        me.cmbSource = Ext.create('Ext.dirac.utils.DiracBoxSelect', {
                    id : 'Source_cmb',
                    name : 'Source',
                    fieldLabel : "Source",
                    queryMode : 'local',
                    labelAlign : 'top',
                    displayField : "text",
                    valueField : "value",
                    anchor : '100%',
                    store : sourceStore
                });

                var desStore = Ext.create('Ext.data.JsonStore', {
                                        fields : ['value', 'text'],
                                        proxy : {
                                                type : 'ajax',
                                                url : GLOBAL.BASE_URL + 'TransferAccounting/getDestination',
                                                reader : {
                                                        type : 'json',
                                                        root : 'result'
                                                }
                                        }
                                });

        me.cmbDestination = Ext.create('Ext.dirac.utils.DiracBoxSelect', {
                    id : 'Destination_cmb',
                    name : 'Destination',
                    fieldLabel : "Destination",
                    queryMode : 'local',
                    labelAlign : 'top',
                    displayField : "text",
                    valueField : "value",
                    anchor : '100%',
                    store : desStore
                            });


                var proStore = Ext.create('Ext.data.JsonStore', {
                                        fields : ['value', 'text'],
                                        proxy : {
                                                type : 'ajax',
                                                url : GLOBAL.BASE_URL + 'TransferAccounting/getProtocol',
                                                reader : {
                                                        type : 'json',
                                                        root : 'result'
                                                }
                                        }
                                });
        me.cmbProtocol = Ext.create('Ext.form.field.ComboBox', {
                    id : 'Protocol_cmb',
                    name : 'Protocol',
                    fieldLabel : "Protocol",
                    queryMode : 'local',
                    labelAlign : 'top',
                    displayField : "text",
                    valueField : "value",
                    anchor : '100%',
                    store : proStore
                });



        var finStore = Ext.create('Ext.data.JsonStore', {
                                        fields : ['value', 'text'],
                                        proxy : {
                                                type : 'ajax',
                                                url : GLOBAL.BASE_URL + 'TransferAccounting/getFinalStatus',
                                                reader : {
                                                        type : 'json',
                                                        root : 'result'
                                                }
                                        }
                                });

        me.cmbFinalStatus = Ext.create('Ext.form.field.ComboBox', {
                    id : 'FinalStatus_cmb',
                    name : 'FinalStatus',
                    fieldLabel : "FinalStatus",
                    queryMode : 'local',
                    labelAlign : 'top',
                    displayField : "text",
                    valueField : "value",
                    anchor : '100%',
                    store : finStore
                });


        me.timeSpanPanel = Ext.create('Ext.panel.Panel', {
                    layout : 'anchor',
                    margin : '15 0 0 0',
                    defaults : {
                        anchor : '100%'
                    },
                    dockedItems : [{
                                xtype : 'toolbar',
                                dock : 'bottom',
                                layout : {
                                    pack : 'center'
                                },
                                items : [{
                                            xtype : 'button',
                                            text : 'Reset Time',
                                            iconCls : 'dirac-icon-reset',
                                            scope : me,
                                            handler : me.__resetTimeSpan
                                        }]
                            }]
                });

        me.cmbTimeSpan = Ext.create('Ext.form.field.ComboBox', {
                    id : 'timespan_cmb',
                    name : 'timeSpan',
                    fieldLabel : 'Time Span',
                    labelAlign : 'top',
                    queryMode : 'local',
                    displayField : "text",
                    valueField : "value",
                    margin : '0 5 0 5',
                    store : new Ext.data.ArrayStore({
                                fields : ['value', 'text'],
                                     data : [[86400, "Last Day"],[604800, "Last Week"],[2592000, "Last Month"],[-1, "Manual Selection"]]
                            }),
                                        listeners : {
                                                 change : function(field, newValue, oldValue, eOpts) {




                                                 me.fromDate.hide();
                                                 me.fromTime.hide();
                                                 me.toDate.hide();
                                                 me.toTime.hide();

                                                switch (newValue) {
                                                 case -1 :

                                                 me.fromDate.show();
                                                 me.fromTime.show();
                                                 me.toDate.show();
                                                 me.toTime.show();
                                                 break;

                                                 } }
                                                 }

                });

        me.fromDate = Ext.create('Ext.form.field.Date', {
                    id : 'from_date',
                    name : 'fromDate',
                    width : 100,
                    format : 'Y-m-d',
                    fieldLabel : 'From',
                    labelAlign : 'top',
                    margin : '0 10 0 0',
                                        hidden : true
                });

        me.fromTime = Ext.create('Ext.form.field.Time', {
                    id : 'from_time',
                    name : 'fromTime',
                    width : 100,
                    format : 'H:i',
                    hidden : true
                });

        me.toDate = Ext.create('Ext.form.field.Date', {
                    id : 'to_date',
                    name : 'toDate',
                    width : 100,
                    format : 'Y-m-d',
                    fieldLabel : 'To',
                    labelAlign : 'top',
                    margin : '0 10 0 0',
                    hidden : true
                });

        me.toTime = Ext.create('Ext.form.field.Time', {
                    id : 'to_time',
                    name : 'toTime',
                    width : 100,
                    format : 'H:i',
                    hidden : true
                });

        var calendarFrom = Ext.create('Ext.panel.Panel', {
                    border : false,
                    margin : '0 5 0 5',
                    layout : {
                        type : 'hbox',
                        align : 'bottom'
                    },
                    items : [me.fromDate, me.fromTime]
                });

        var calendarTo = Ext.create('Ext.panel.Panel', {
                    border : false,
                    margin : '0 5 5 5',
                    layout : {
                        type : 'hbox',
                        align : 'bottom'
                    },
                    items : [me.toDate, me.toTime]
                });
        me.btnTest = new Ext.Button({
              tooltip : 'it is testing the button',
              text : 'submit',
              margin : 3,
              iconCls : "dirac-icon-reset",
              handler : function() {

                me.leftPanel.body.mask("Wait ...");
                Ext.Ajax.request({
                      url : GLOBAL.BASE_URL + 'TransferAccounting/getSelectData',
                      method : 'POST',
                      scope : me,
                      success : function(response) {

                        var oResult = Ext.JSON.decode(response.responseText);

                        if (oResult["success"] == "true")
                          alert(oResult["result"]);
                        else
                          alert(oResult["error"]+'eeeeeeeee');
                        me.leftPanel.body.unmask();
                      },
                      failure : function(response, opt) {
                        GLOBAL.APP.CF.showAjaxErrorMessage(response);
                        me.rightPanel.body.unmask();
                        me.leftPanel.body.unmask();
                      }
                    });

              },
              scope : me

            });

        me.btnPlot = new Ext.Button({
                  tooltip : 'It creates a new plot',
                  text : 'new test',
                  margin : 3,
                  iconCls : "accp-submit-icon",
                  handler : me.__generatePlott,
              scope : me
            });

       /* me.oImage = Ext.create('Ext.Img', {
 *             width:800,
 *                     height:600,
 *                             src: 'https://www.sencha.com/img/20110215-feat-html5.png',
 *                                         scope:me
 *                                                });
 *                                                       */




        me.timeSpanPanel.add(me.cmbTimeSpan, calendarFrom, calendarTo);
                me.leftPanel.add( me.cmbPlotName, me.cmbGrouping, me.cmbUser, me.cmbSource,
                        me.cmbDestination, me.cmbProtocol, me.cmbFinalStatus, me.timeSpanPanel);


        me.add(me.leftPanel, me.rightPanel);
    },

    __generatePlot:function(){
        var me = this;
        var selectors = me.__getSelector();
        var params = me.__generPostParam(selectors);
        alert(params['_startTime'])
    me.leftPanel.body.mask("Wait ...");

    Ext.Ajax.request({
                     url : GLOBAL.BASE_URL + 'TransferAccounting/generatePlot',
                      method : 'POST',
                      params : params,
                      scope : me,
                      success : function(response) {

                        var oResult = Ext.JSON.decode(response.responseText);

                        if (oResult["success"] == "true")
                          alert(oResult["result"]);
                        else
                          alert(oResult["error"]);
                        me.leftPanel.body.unmask();
                      },
                      failure : function(response, opt) {
                        GLOBAL.APP.CF.showAjaxErrorMessage(response);
                        me.rightPanel.body.unmask();
                        me.leftPanel.body.unmask();
                      }
                    });

    },

    __generatePlott:function(){
        var me = this;
        var selectors = me.__getSelector();
        var params = me.__generPostParam(selectors);

        me.leftPanel.body.mask("Wait ...");

        Ext.Ajax.request({
                     url : GLOBAL.BASE_URL + 'TransferAccounting/generatePlot',
                      method : 'POST',
                      params : params,
                      scope : me,
                      success : function(response) {

                        var oResult = Ext.JSON.decode(response.responseText);

                        if (oResult["success"] == "true"){

              var src = GLOBAL.BASE_URL + "TransferAccounting/getPlotImg?file=" + oResult["result"];

              me.oImage = Ext.create('Ext.Img', {
                                  width:800,
                            height:600,
                             src: 'https://www.sencha.com/img/20110215-feat-html5.png',
                                   scope:me
                                    });
                          var chartPanel = Ext.create('Ext.panel.Panel', {
                    title :  me.cmbPlotName.getValue()+' by '+me.cmbGrouping.getValue(),
                    closable : true,
                    });
                      chartPanel.add(me.oImage);
                          me.rightPanel.add(chartPanel);
              me.oImage.setSrc(src);
                          me.leftPanel.body.unmask();
            }
                        else
                          alert(oResult["error"]);
                        me.leftPanel.body.unmask();
                      },
                      failure : function(response, opt) {
                        GLOBAL.APP.CF.showAjaxErrorMessage(response);
                        me.rightPanel.body.unmask();
                        me.leftPanel.body.unmask();
                      }
                    });

    },


    __getSelector : function() {
        var me = this;

        selectors = {}

        var group = me.cmbGrouping.getValue();
        if (group == null) {
            Ext.MessageBox.alert('warn', 'Please choose the group!');
            return null;
        }

        var plotname = me.cmbPlotName.getValue();
        if (plotname == null) {
            Ext.MessageBox.alert('warn', 'Please choose the plot name!');
            return null;
        }

        var timeSpan = me.cmbTimeSpan.getValue();
        var fromDate = me.fromDate.getValue();
        var fromTime = me.fromTime.getValue();
        var toDate = me.toDate.getValue();
        var toTime = me.toTime.getValue();
        if (timeSpan == null && fromDate == null) {
            Ext.MessageBox.alert('warn', 'Please choose from date!');
            return null;
        }

        selectors[me.cmbGrouping.getId()] = group;
        selectors[me.cmbPlotName.getId()] = plotname;
        selectors[me.cmbTimeSpan.getId()] = timeSpan;
        selectors[me.fromDate.getId()] = fromDate;
        selectors[me.fromTime.getId()] = fromTime;
        selectors[me.toDate.getId()] = toDate;
        selectors[me.toTime.getId()] = toTime;
                var sour=me.cmbSource.getValue();
                   selectors[me.cmbSource.getId()]=sour;

            var des=me.cmbDestination.getValue();
            selectors[me.cmbDestination.getId()]=des;

            var pro=me.cmbProtocol.getValue();
            selectors[me.cmbProtocol.getId()]=pro;

            var user=me.cmbUser.getValue();
            selectors[me.cmbUser.getId()]=user;

        var fina=me.cmbFinalStatus.getValue();
                   selectors[me.cmbFinalStatus.getId()]=fina;
        return selectors;
    },

    __generPostParam : function(selectors) {
        var me = this;

        var post = {};
                if(selectors[me.cmbSource.getId()]!=null){
        post['_Source']=selectors[me.cmbSource.getId()];

                }

        if(selectors[me.cmbDestination.getId()]!=null){
        post['_Destination']=selectors[me.cmbDestination.getId()];}

        if(selectors[me.cmbProtocol.getId()]!=null){
        post['_Protocol']=selectors[me.cmbProtocol.getId()];}

        if(selectors[me.cmbUser.getId()]!=null){
        post['_User']=selectors[me.cmbUser.getId()];}

                if(selectors[me.cmbFinalStatus.getId()]!=null){
                post['_FinalStatus']=selectors[me.cmbFinalStatus.getId()];}

        post['_grouping'] = selectors[me.cmbGrouping.getId()];
        post['_plotName'] = selectors[me.cmbPlotName.getId()];
            post['_typeName'] = "DataTransfer"
        function pad(num) {
            if (num < 10)
                num = '0' + num;
            return num;
        }

        var timeSpan = selectors[me.cmbTimeSpan.getId()];
        var now = new Date();
        if (timeSpan == -1) {
            var fromDate = selectors[me.fromDate.getId()];
            var fromDateStr = fromDate.getFullYear() + '-'
                    + pad(fromDate.getMonth() + 1) + '-'
                    + pad(fromDate.getDate());
            var fromTime = me.fromTime.getValue();
            if (fromTime == null)
                from = fromDateStr + ' 00:00';
            else
                from = fromDateStr + ' ' + pad(fromTime.getHours()) + ':'
                        + pad(fromTime.getMinutes());

            var toDate = me.toDate.getValue();
            if (toDate == null) {
                to = now.getUTCFullYear() + '-' + pad(now.getUTCMonth() + 1)
                        + '-' + pad(now.getUTCDate()) + ' '
                        + pad(now.getUTCHours()) + ':'
                        + pad(now.getUTCMinutes());
            } else {
                var toDateStr = toDate.getFullYear() + '-'
                        + pad(toDate.getMonth() + 1) + '-'
                        + pad(toDate.getDate());
                var toTime = me.toTime.getValue();
                if (toTime == null)
                    to = toDateStr + ' 00:00';
                else
                    to = toDateStr + ' ' + pad(toTime.getHours()) + ':'
                            + pad(toTime.getMinutes());
            }
        } else {
            var now = new Date();
            var to = now.getUTCFullYear() + '-' + pad(now.getUTCMonth() + 1)
                    + '-' + pad(now.getUTCDate()) + ' '
                    + pad(now.getUTCHours()) + ':' + pad(now.getUTCMinutes());
            now.setSeconds(now.getSeconds() - String(timeSpan));
            var from = now.getUTCFullYear() + '-' + pad(now.getUTCMonth() + 1)
                    + '-' + pad(now.getUTCDate()) + ' '
                    + pad(now.getUTCHours()) + ':' + pad(now.getUTCMinutes());
        }

        post['_startTime'] = from;
        post['_endTime'] = to;

        return post;
    },


    __reset : function() {
        var me = this;
        me.cmbGrouping.setValue(null);
        me.cmbPlotName.setValue(null);
        me.__resetTimeSpan();
    },

    __resetTimeSpan : function() {
        var me = this;
        me.cmbTimeSpan.setValue(null);
        me.fromDate.setValue(null);
        me.fromTime.setValue(null);
        me.toDate.setValue(null);
        me.toTime.setValue(null);
    },

    __submit : function() {
        var me = this;
        me.__generatePlott();
    },

    __refresh : function() {
        var me = this;
        me.__generatePlott();
    },



});
