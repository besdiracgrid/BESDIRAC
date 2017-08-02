Ext.define('BESDIRAC.SiteStatusMonitor.classes.SiteStatusMonitor', {
	extend : 'Ext.dirac.core.Module',
	requires : [],

	dataFields : [{
				name : 'Site'
			}, {
				name : 'SiteType'
			}, {
				name : 'Icon',
				mapping : 'MaskStatus'
			}, {
				name : 'MaskStatus'
			}, {
				name : 'VO'
			}, {
				name : 'CEStatus'
			}, {
				name : 'SEStatus'
			}, {
				name : 'MaxStorage'
			}, {
				name : 'FreeStorage'
			}, {
				name : 'StorageUsage'
			}, {
				name : 'Efficiency'
			}, {
				name : 'Running'
			}, {
				name : 'Waiting'
			}, {
				name : 'Done'
			}, {
				name : 'Failed'
			}, {
				name : 'MaxJobs'
			}, {
				name : 'JobUsage'
			}, {
				name : 'WNStatus'
			}],

	initComponent : function() {
		var me = this;

		me.launcher.title = 'Site Status Monitor';
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

		var selectors = {
			site : 'Site',
			type : 'Site Type',
			mask : 'Mask Status',
			vo : 'VO'
		};

		var map = [['site', 'site'], ['type', 'type'], ['mask', 'mask'],
				['vo', 'vo']]

		me.leftPanel = Ext.create('Ext.dirac.utils.DiracBaseSelector', {
					scope : me,
					cmbSelectors : selectors,
					hasTimeSearchPanel : false,
					datamap : map,
					url : me.applicationName + '/getSelectionData'
				});
		me.leftPanel.__loadSelectorData = function() {
			var me = this;

			if (Object.keys(me.cmbSelectors).length > 0) {
				Ext.Ajax.request({
							url : GLOBAL.BASE_URL + me.url,
							params : {},
							scope : me,
							success : function(response) {

								var me = this;
								var response = Ext.JSON
										.decode(response.responseText);

								if (response.success == "false") {
									Ext.dirac.system_info.msg("Error",
											response.error);
									return;
								}

								me.__oprRefreshStoresForSelectors(
										response.result, false);

								if ('defaultVO' in response) {
									me.cmbSelectors.vo
											.setValue(response.defaultVO);
								}

								me.bDataSelectionLoaded = true;
							},
							failure : function(response) {
								GLOBAL.APP.CF.showAjaxErrorMessage(response);
							}
						});
			}
		}

		var oColumns = {
			'Site' : {
				'dataIndex' : 'Site',
				'properties' : {
					width : 120
				}
			},
			'SiteType' : {
				'dataIndex' : 'SiteType',
				'properties' : {
					width : 80
				}
			},
			'None2' : {
				'dataIndex' : 'Icon',
				'properties' : {
					width : 26,
					sortable : false,
					hideable : false,
					fixed : true,
					menuDisabled : true
				},
				'renderFunction' : 'rendererStatus'
			},
			'MaskStatus' : {
				'dataIndex' : 'MaskStatus',
				'properties' : {
					width : 80
				}
			},
			'VO' : {
				'dataIndex' : 'VO',
				'properties' : {
					width : 50,
					hidden : true
				}
			},
			'CE-Test' : {
				'dataIndex' : 'CEStatus',
				'properties' : {
					width : 60
				},
				'renderer' : me.__renderStatus
			},
			'SE-Test' : {
				'dataIndex' : 'SEStatus',
				'properties' : {
					width : 60
				},
				'renderer' : me.__renderStatus
			},
			'Max Storage(GB)' : {
				'dataIndex' : 'MaxStorage',
				'properties' : {
					width : 100,
					hidden : true
				}
			},
			'Free Storage(GB)' : {
				'dataIndex' : 'FreeStorage',
				'properties' : {
					width : 100,
					hidden : true
				}
			},
			'Storage Usage(%)' : {
				'dataIndex' : 'StorageUsage',
				'properties' : {
					width : 105
				},
				'renderer' : me.__renderRateDSCE
			},
			'Efficiency(%)' : {
				'dataIndex' : 'Efficiency',
				'properties' : {
					width : 80
				},
				'renderer' : me.__renderRateASCE
			},
			'R' : {
				'dataIndex' : 'Running',
				'properties' : {
					width : 40,
					hidden : true
				}
			},
			'W' : {
				'dataIndex' : 'Waiting',
				'properties' : {
					width : 40,
					hidden : true
				}
			},
			'D' : {
				'dataIndex' : 'Done',
				'properties' : {
					width : 40,
					hidden : true
				}
			},
			'F' : {
				'dataIndex' : 'Failed',
				'properties' : {
					width : 40,
					hidden : true
				}
			},
			'Max Jobs' : {
				'dataIndex' : 'MaxJobs',
				'properties' : {
					width : 60,
					hidden : true
				}
			},
			'Job Usage(%)' : {
				'dataIndex' : 'JobUsage',
				'properties' : {
					width : 85
				},
				'renderer' : me.__renderRateDSCE
			},
			'WN Status' : {
				'dataIndex' : 'WNStatus',
				'properties' : {
					width : 65
				},
				'renderer' : me.__renderStatus
			}
		};

		var oproxy = Ext.create('Ext.dirac.utils.DiracAjaxProxy', {
					url : GLOBAL.BASE_URL + me.applicationName + '/getMainData'
				});

		me.datastore = Ext.create('Ext.dirac.utils.DiracJsonStore', {
					proxy : oproxy,
					fields : me.dataFields,
					scope : me,
					remoteSort : false
				});

		var pagingToolbar = Ext.create('Ext.dirac.utils.DiracPagingToolbar', {
					store : me.datastore,
					scope : me,
					value : 25
				});

		var menuitems = {
			'Visible' : [{
						'text' : 'SAM Information',
						'handler' : me.__oprShowSAMInformation,
						'properties' : {
							id : 'SAMInformation',
							tooltip : 'Click to show SAM information.'
						}
					}, {
						'text' : 'Host Information',
						'handler' : me.__oprShowHostInformation,
						'properties' : {
							id : 'HostInformation',
							tooltip : 'Click to show Host Job Information.'
						}
					}]
		};

		me.contextGridMenu = Ext.create(
				'Ext.dirac.utils.DiracApplicationContextMenu', {
					menu : menuitems,
					scope : me
				});

		me.grid = Ext.create('Ext.dirac.utils.DiracGridPanel', {
					columnLines : true,
					oColumns : oColumns,
					pagingToolbar : pagingToolbar,
					contextMenu : me.contextGridMenu,
					store : me.datastore,
					scope : me
				});

		me.leftPanel.setGrid(me.grid);
		me.add([me.leftPanel, me.grid]);
	},

	__oprShowSAMInformation : function() {
		var me = this;

		var oVO = me.leftPanel.cmbSelectors.vo.getValue();
		var oSite = GLOBAL.APP.CF.getFieldValueFromSelectedRow(me.grid, 'Site');
		if (oVO.length == 0) {
			var oParams = {
				site : '["' + oSite + '"]'
			};
		} else {
			var oParams = {
				site : '["' + oSite + '"]',
				vo : '["' + oVO[0] + '"]'
			};
		}
		Ext.Ajax.request({
					url : GLOBAL.BASE_URL + me.applicationName + '/getSAMData',
					params : oParams,
					method : 'POST',
					scope : me,
					success : function(response) {
						var jsonData = Ext.JSON.decode(response.responseText);

						if (jsonData.success == 'false') {
							GLOBAL.APP.CF.msg("error", jsonData.error);
						} else {
							var oWindow = me.getContainer().createChildWindow(
									'SAM Information - ' + oSite, false, 600,
									300);

							var oFields = ['ElementName', 'ElementType',
									'Status'].concat(jsonData.columns);
							var oData = jsonData.result;
							var oStore = new Ext.data.Store({
										fields : oFields,
										data : oData
									});

							var oColumns = [{
										text : 'ElementName',
										flex : 1.2,
										dataIndex : 'ElementName'
									}, {
										text : 'ElementType',
										flex : 1,
										dataIndex : 'ElementType'
									}, {
										text : 'Status',
										flex : 1,
										dataIndex : 'Status',
										renderer : me.__renderStatus
									}];
							for (var i in jsonData.columns) {
								var colName = jsonData.columns[i];
								oColumns.push({
											text : colName.split('-')[0],
											flex : 1,
											dataIndex : colName,
											renderer : me.__renderStatus
										});
							}

							var oGrid = Ext.create('Ext.grid.Panel', {
										store : oStore,
										region : 'center',
										columns : oColumns,
										viewConfig : {
											stripeRows : true,
											enableTextSelection : true
										}
									});
							oGrid.on('cellclick', me.__showSAMDetail, me);

							oWindow.add(oGrid);
							oWindow.show();
						}
					},
					failure : function(response) {
						GLOBAL.APP.CF.showAjaxErrorMessage(response);
					}
				});
	},

	__showSAMDetail : function(view, td, cellIndex, record, tr, rowIndex, e) {
		var me = this;

		if (cellIndex >= 2) {
			var oGrid = view.up('gridpanel');
			var oTestType = oGrid.columns[cellIndex].dataIndex;
			var oElementName = record.get(oGrid.columns[0].dataIndex);

			if (record.get(oTestType)) {
				Ext.Ajax.request({
					url : GLOBAL.BASE_URL + me.applicationName
							+ '/getSAMDetail',
					params : {
						elementName : oElementName,
						testType : oTestType
					},
					method : 'POST',
					scope : me,
					success : function(response) {
						var jsonData = Ext.JSON.decode(response.responseText);

						if (jsonData.success == 'false') {
							GLOBAL.APP.CF.msg("error", jsonData.error);
						} else {
							var oData = jsonData.result;
							var oWindow = me.getContainer().createChildWindow(
									oElementName + ' - ' + oTestType, false,
									640, 480);
							var oForm = Ext.create('Ext.form.Panel', {
										title : 'SAM Detail Information',
										defaults : {
											labelAlign : 'right',
											margin : '5 10 5 10',
											anchor : '100%',
											readOnly : true
										},
										items : [{
													xtype : 'textfield',
													name : 'testType',
													fieldLabel : 'TestType',
													value : oData.TestType
												}, {
													xtype : 'textfield',
													name : 'elementName',
													fieldLabel : 'ElementName',
													value : oData.ElementName
												}, {
													xtype : 'textfield',
													name : 'elementType',
													fieldLabel : 'ElementType',
													value : oData.ElementType
												}, {
													xtype : 'textfield',
													name : 'submissionTime',
													fieldLabel : 'SubmissionTime',
													value : oData.SubmissionTime
												}, {
													xtype : 'textfield',
													name : 'completionTime',
													fieldLabel : 'CompletionTime',
													value : oData.CompletionTime
												}, {
													xtype : 'textfield',
													name : 'applicationTime',
													fieldLabel : 'ApplicationTime',
													value : oData.ApplicationTime
												}, {
													xtype : 'textfield',
													name : 'status',
													fieldLabel : 'Status',
													value : oData.Status
												}, {
													xtype : 'textareafield',
													name : 'log',
													fieldLabel : 'Log',
													anchor : '100% -190',
													value : oData.Log
												}]
									});

							oWindow.add(oForm);
							oWindow.show();
						}
					},
					failure : function(response) {
						GLOBAL.APP.CF.showAjaxErrorMessage(response);
					}
				});
			}
		}
	},

	__oprShowHostInformation : function(grid, record) {
		var me = this;

		var oSite = GLOBAL.APP.CF.getFieldValueFromSelectedRow(me.grid, 'Site');
		Ext.Ajax.request({
					url : GLOBAL.BASE_URL + me.applicationName
							+ '/getWorkNodeData',
					params : {
						site : '["' + oSite + '"]'
					},
					method : 'POST',
					scope : me,
					success : function(response) {
						var jsonData = Ext.JSON.decode(response.responseText);

						if (jsonData.success == 'false') {
							GLOBAL.APP.CF.msg("error", jsonData.error);
						} else {
							var oWindow = me.getContainer().createChildWindow(
									'Host Information - ' + oSite, false, 500,
									300);

							var oFields = ['Host', 'Done', 'Failed',
									'Efficiency'];
							var oData = jsonData.result;
							var oStore = new Ext.data.Store({
										fields : oFields,
										data : oData
									});

							var oColumns = [{
										text : 'Host',
										flex : 1.2,
										dataIndex : 'Host'
									}, {
										text : 'Done',
										flex : 1,
										dataIndex : 'Done'
									}, {
										text : 'Failed',
										flex : 1,
										dataIndex : 'Failed'
									}, {
										text : 'Efficiency',
										flex : 1,
										dataIndex : 'Efficiency'
									}];

							var oGrid = Ext.create('Ext.grid.Panel', {
										store : oStore,
										region : 'center',
										columns : oColumns,
										viewConfig : {
											stripeRows : true,
											enableTextSelection : true
										}
									});

							oWindow.add(oGrid);
							oWindow.show();
						}
					},
					failure : function(response) {
						GLOBAL.APP.CF.showAjaxErrorMessage(response);
					}
				})
	},

	__renderStatus : function(v) {
		switch (v) {
			case 'OK' :
				return '<font color="green">' + v + '</font>';
			case 'Busy' :
				return '<font color="purple">' + v + '</font>';
			case 'Warn' :
				return '<font color="orange">' + v + '</font>';
			case 'Bad' :
				return '<font color="red">' + v + '</font>';
			case 'Unknown' :
				return '<font color="blue">' + v + '</font>';
			default :
				return '<font color="black">' + v + '</font>';
		}
	},

	__renderRateASCE : function(v) {
		if (v >= 80)
			return '<font color="green">' + v + '</font>';
		if (v <= 50)
			return '<font color="red">' + v + '</font>';
		return '<font color="orange">' + v + '</font>';
	},

	__renderRateDSCE : function(v) {
		if (v <= 50)
			return '<font color="green">' + v + '</font>';
		if (v >= 80)
			return '<font color="red">' + v + '</font>';
		return '<font color="orange">' + v + '</font>';
	}

});
