Ext.define('BESDIRAC.SAMHistory.classes.SAMHistory', {
	extend : 'Ext.dirac.core.Module',

	requires : [],

	initComponent : function() {
		var me = this;

		me.launcher.title = 'SAM History';
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
						tabchange : function(tabPanel, newPanel) {
							var selectors = newPanel.selectors;
							me.__setSelectors(selectors);
						}
					}
				});

		me.cmbCategory = Ext.create('Ext.form.field.ComboBox', {
					id : 'category_cmb',
					name : 'category',
					fieldLabel : "Category",
					queryMode : 'local',
					labelAlign : 'top',
					displayField : "text",
					valueField : "value",
					anchor : '100%',
					store : new Ext.data.ArrayStore({
								fields : ['value', 'text'],
								data : [['Availability', 'Availability'],
										['SAMStatus', 'SAM Status'],
										['TestResults', 'Test Results']]
							})
				});

		me.cmbType = Ext.create('Ext.form.field.ComboBox', {
					id : 'type_cmb',
					name : 'elementType',
					fieldLabel : "Element Type",
					queryMode : 'local',
					labelAlign : 'top',
					displayField : "text",
					valueField : "value",
					anchor : '100%',
					store : new Ext.data.ArrayStore({
								fields : ['value', 'text'],
								data : [
										['Site', 'Site'],
										['ComputingElement', 'ComputingElement'],
										['StorageElement', 'StorageElement']]
							}),
					listeners : {
						change : function(field, newValue, oldValue, eOpts) {
							me.cmbElement.clearValue();
							me.cmbElement.getStore().load({
										params : {
											elementType : newValue
										}
									});
						}
					}
				});

		var elementStore = Ext.create('Ext.data.JsonStore', {
					fields : ['value', 'text'],
					proxy : {
						type : 'ajax',
						url : GLOBAL.BASE_URL + me.applicationName
								+ '/getElements',
						reader : {
							type : 'json',
							root : 'result'
						}
					}
				});

		me.cmbElement = Ext.create('Ext.dirac.utils.DiracBoxSelect', {
					id : 'element_cmb',
					name : 'elements',
					fieldLabel : "Element",
					queryMode : 'local',
					labelAlign : 'top',
					displayField : "text",
					valueField : "value",
					anchor : '100%',
					store : elementStore
				});

		me.cmbVO = Ext.create('Ext.form.field.ComboBox', {
					id : 'vo_cmb',
					name : 'vo',
					fieldLabel : 'VO',
					queryMode : 'local',
					labelAlign : 'top',
					displayField : 'text',
					valueField : 'value',
					anchor : '100%',
					listeners : {
						scope : me,
						afterrender : me.__setVO
					}
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
								data : [[86400, "Last Day"],
										[604800, "Last Week"],
										[2592000, "Last Month"]]
							})
				});

		me.fromDate = Ext.create('Ext.form.field.Date', {
					id : 'from_date',
					name : 'fromDate',
					width : 100,
					format : 'Y-m-d',
					fieldLabel : 'From',
					labelAlign : 'top',
					margin : '0 10 0 0'
				});

		me.fromTime = Ext.create('Ext.form.field.Time', {
					id : 'from_time',
					name : 'fromTime',
					width : 100,
					format : 'H:i'
				});

		me.toDate = Ext.create('Ext.form.field.Date', {
					id : 'to_date',
					name : 'toDate',
					width : 100,
					format : 'Y-m-d',
					fieldLabel : 'To',
					labelAlign : 'top',
					margin : '0 10 0 0'
				});

		me.toTime = Ext.create('Ext.form.field.Time', {
					id : 'to_time',
					name : 'toTime',
					width : 100,
					format : 'H:i'
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

		me.timeSpanPanel.add(me.cmbTimeSpan, calendarFrom, calendarTo);
		me.leftPanel.add(me.cmbCategory, me.cmbType, me.cmbElement, me.cmbVO,
				me.timeSpanPanel);
		me.add(me.leftPanel, me.rightPanel);
	},

	__setVO : function(cmb) {
		var me = this;

		Ext.Ajax.request({
					url : GLOBAL.BASE_URL + me.applicationName + '/getVOs',
					method : 'GET',
					scope : me,
					success : function(response) {
						var jsonData = Ext.JSON.decode(response.responseText);

						if (jsonData.success == 'false') {
							GLOBAL.APP.CF.msg("error", jsonData.error);
						} else {
							var oData = [];
							for (var i in jsonData.result.VOs) {
								var vo = jsonData.result.VOs[i];
								oData.push([vo, vo]);
							}

							var voStore = new Ext.data.ArrayStore({
										fields : ['value', 'text'],
										data : oData
									});

							me.cmbVO.store = voStore;
							me.defaultVO == jsonData.result.defaultVO;
							if (me.defaultVO != '') {
								me.cmbVO.setValue(jsonData.result.defaultVO);
							}
						}
					},
					failed : function(response) {
						var errorMsg = 'HTTP Error(' + response.status + ') : '
								+ response.statusText;
						Ext.MessageBox.alert('error', errorMsg);
					}
				});
	},

	__reset : function() {
		var me = this;
		me.cmbCategory.setValue(null);
		me.cmbType.setValue(null);
		me.cmbElement.setValue(null);
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
		me.__plot(true);
	},

	__refresh : function() {
		var me = this;
		me.__plot(false);
	},

	__plot : function(plotInNew) {
		var me = this;

		var selectors = me.__getSelectors();
		var params = me.__generPostParams(selectors);

		me.rightPanel.body.mask("Wait ...");
		Ext.Ajax.request({
			url : GLOBAL.BASE_URL + me.applicationName + '/getPlotData',
			method : 'POST',
			params : params,
			scope : me,
			success : function(response) {
				var respText = Ext.decode(response.responseText);

				if (respText.success == 'false') {
					var errorMsg = 'Service Error : ' + respText.error;
					Ext.MessageBox.alert('error', errorMsg);
				} else {
					var title = me.cmbType.getRawValue() + ' '
							+ me.cmbCategory.getRawValue();
					if (plotInNew) {
						var chartPanel = Ext.create('Ext.panel.Panel', {
									title : title,
									closable : true,
									selectors : selectors
								});
						me.rightPanel.add(chartPanel);
					} else {
						var chartPanel = me.rightPanel.getActiveTab();
					}

					if (params.category == 'Availability') {
						var summaryChar = new Highcharts.chart({
									chart : {
										type : 'bar',
										renderTo : chartPanel.id + '-body',
										marginRight : 10
									},
									title : {
										text : title,
										style : {
											fontWeight : 'bold'
										}
									},
									subtitle : {
										text : 'from ' + params.from + ' to '
												+ params.to
									},
									xAxis : {
										categories : respText.elements
									},
									yAxis : {
										min : 0,
										max : 100,
										title : {
											text : 'Availability(%)',
											style : {
												fontSize : '16px',
												fontWeight : 'bold',
												color : '#333333'
											}
										}
									},
									tooltip : {
										formatter : function() {
											return '<b>' + this.x + ' : '
													+ this.y + '%' + '</b>';
										}
									},
									legend : {
										enabled : false
									},
									series : [{
												data : respText.result
											}]
								});
					} else {
						detailData = [];
						for (var i = 0; i < respText.result.length; i++) {
							for (var j = 0; j < respText.result[i].length; j++) {
								var rate = respText.result[i][j];
								var point = {
									x : j,
									y : i
								};
								if (rate == null) {
									point.color = 'white';
									point.value = '';
								} else if (rate == -1) {
									point.color = 'blue';
									point.value = 'Unknown';
								} else if (rate == -2) {
									point.color = 'purple';
									point.value = 'Busy';
								} else {
									point.value = rate;
								}
								detailData.push(point);
							}
						}
						var detailChart = new Highcharts.chart({
							chart : {
								type : 'heatmap',
								renderTo : chartPanel.id + '-body'
							},
							title : {
								text : title + ' History',
								style : {
									fontWeight : 'bold'
								}
							},
							subtitle : {
								text : 'from ' + params.from + ' to '
										+ params.to
							},
							xAxis : {
								categories : respText.timestamps,
								title : {
									text : 'Datetime(UTC)',
									style : {
										fontSize : '16px',
										fontWeight : 'bold',
										color : '#333333'
									}
								}
							},
							yAxis : {
								categories : respText.elements,
								title : false
							},
							colorAxis : {
								stops : [[0, '#FF0000'], [0.5, '#FFFF00'],
										[1, '#006600']],
								min : 0,
								max : 1,
								reversed : false
							},
							legend : {
								align : 'right',
								layout : 'vertical',
								margin : 0,
								verticalAlign : 'top',
								y : 42,
								symbolHeight : chartPanel.getHeight() - 156
							},
							tooltip : {
								formatter : function() {
									return '<b>'
											+ this.series.yAxis.categories[this.point.y]
											+ '</b><br><b>Availability:'
											+ this.point.value
											+ '</b><br><b>At '
											+ this.series.xAxis.categories[this.point.x]
											+ '</b>';
								}
							},
							plotOptions : {
								series : {
									turboThreshold : 0
								}
							},
							series : [{
										borderWidth : 0.5,
										data : detailData
									}]
						});
					}
				}
				me.rightPanel.body.unmask();
			},
			failure : function(response) {
				var errorMsg = 'HTTP Error(' + response.status + ') : '
						+ response.statusText;
				Ext.MessageBox.alert('error', errorMsg);
				me.rightPanel.body.unmask();
			}
		});
	},

	__setSelectors : function(selectors) {
		var me = this;

		me.cmbCategory.setValue(selectors[me.cmbCategory.getId()]);
		me.cmbType.setValue(selectors[me.cmbType.getId()]);
		me.cmbElement.setValue(selectors[me.cmbElement.getId()]);
		me.cmbVO.setValue(selectors[me.cmbVO.getId()]);
		me.cmbTimeSpan.setValue(selectors[me.cmbTimeSpan.getId()]);
		me.fromDate.setValue(selectors[me.fromDate.getId()]);
		me.fromTime.setValue(selectors[me.fromTime.getId()]);
		me.toDate.setValue(selectors[me.toDate.getId()]);
		me.toTime.setValue(selectors[me.toTime.getId()]);
	},

	__getSelectors : function() {
		var me = this;

		selectors = {}

		var category = me.cmbCategory.getValue();
		if (category == null) {
			Ext.MessageBox.alert('warn', 'Please chose the category!');
			return null;
		}

		var elementType = me.cmbType.getValue();
		if (elementType == null) {
			Ext.MessageBox.alert('warn', 'Please chose the element type!');
			return null;
		}

		var elements = me.cmbElement.getValue();
		if (category == 'TestResults' && elements.length != 1) {
			Ext.MessageBox.alert('warn', 'Please chose one element!');
			return null;
		}

		var vo = me.cmbVO.getValue();

		var timeSpan = me.cmbTimeSpan.getValue();
		var fromDate = me.fromDate.getValue();
		var fromTime = me.fromTime.getValue();
		var toDate = me.toDate.getValue();
		var toTime = me.toTime.getValue();
		if (timeSpan == null && fromDate == null) {
			Ext.MessageBox.alert('warn', 'Please chose from date!');
			return null;
		}

		selectors[me.cmbCategory.getId()] = category;
		selectors[me.cmbType.getId()] = elementType;
		selectors[me.cmbElement.getId()] = elements;
		selectors[me.cmbVO.getId()] = vo;
		selectors[me.cmbTimeSpan.getId()] = timeSpan;
		selectors[me.fromDate.getId()] = fromDate;
		selectors[me.fromTime.getId()] = fromTime;
		selectors[me.toDate.getId()] = toDate;
		selectors[me.toTime.getId()] = toTime;

		return selectors;
	},

	__generPostParams : function(selectors) {
		var me = this;

		var post = {};
		post['category'] = selectors[me.cmbCategory.getId()];
		post['elementType'] = selectors[me.cmbType.getId()];
		post['elements'] = selectors[me.cmbElement.getId()];
		post['vo'] = selectors[me.cmbVO.getId()];

		function pad(num) {
			if (num < 10)
				num = '0' + num;
			return num;
		}

		var timeSpan = selectors[me.cmbTimeSpan.getId()];
		var now = new Date();
		if (timeSpan == null) {
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

		post['from'] = from;
		post['to'] = to;

		return post;
	}
});
