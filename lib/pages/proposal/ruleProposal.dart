import 'dart:convert';

import 'package:cfapi/services/rule.dart';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class RuleProposal extends StatefulWidget {
  @override
  _RuleProposalState createState() => _RuleProposalState();
}

class _RuleProposalState extends State<RuleProposal> {
  String _ST='';
  bool _mod=true;
  int _trl;
  List<String> _filters = <String>[];
  List<Rule> _rules=<Rule>[];
  final TextEditingController _srCtl = TextEditingController();
  final TextEditingController _keyCtl = TextEditingController();

  void ruleQuery(Map data) async{
    List<Rule> rules=await Rule.query(data);
    setState(() {
      _rules= rules;
    });
  }

  final List<String> dept=["管理人员","客管部","客服部","技术部","计划部","采购部","仓库","发货","金工部","电机","下线","电气部","装泵","电焊","工程部","质量部","IT部","人力部","后勤部","财务部","统计部","市场部","招商部"];
  final List<String> xz=["经济/成本","目标达成","质量","效率","规定","设备/工具","加班/值班","建议/创新","6S","会议/培训","考勤","仪表","活动","荣誉","自主学习","品行"];  
  
  Iterable<Widget> get deptWidgets sync* {
    for (int i=0;i<dept.length;i++) {
      yield Padding(
        padding: const EdgeInsets.all(4.0),
        child: FilterChip(
          avatar: CircleAvatar(),
          label: Text(dept[i]),
          selected: _filters.contains(dept[i]),
          onSelected: (bool value) {
            setState(() {
              if (value) {
                _filters.add(dept[i]);
              } else {
                _filters.removeWhere((String name) {
                  return name == dept[i];
                });
              }
            });
          },
        ),
      );
    }
  }

  Iterable<Widget> get xzWidgets sync* {
    for (int i=0;i<xz.length;i++) {
      yield Padding(
        padding: const EdgeInsets.all(4.0),
        child: FilterChip(
          avatar: CircleAvatar(backgroundColor: Colors.red),
          label: Text(xz[i]),
          selected: _filters.contains(xz[i]),
          onSelected: (bool value) {            
            print(_filters.toString());
            setState(() {
              if (value) {
                _filters.add(xz[i]);
              } else {
                _filters.removeWhere((String name) {
                  return name == xz[i];
                });
              }
            });            
          },
        ),
      );
    }
  }
  Column filter()=>Column(
    children:<Widget>[
      SwitchListTile(
        inactiveThumbColor: Colors.red,
        title: _mod?
          Text('按部门搜索',style: TextStyle(color:Colors.blue,fontWeight:FontWeight.bold)):
          Text('按积分规则属性搜索',style: TextStyle(color:Colors.red,fontWeight:FontWeight.bold)),
        value: _mod,
        onChanged: (bool value) {
          setState(() {
             _mod = value;
             _filters=[];
          }); 
        },
        secondary: _mod? 
          Icon(Icons.dns, color: Colors.blue):
          Icon(Icons.assignment, color: Colors.red),
      ),
      Wrap(
        spacing: 8.0, // gap between adjacent chips
        runSpacing: 4.0, 
        children: _mod? deptWidgets.toList():xzWidgets.toList()
      ),
      SizedBox(height:30),
      Row(
        children:<Widget>[
          Expanded(                
            child: Padding(
              padding: EdgeInsets.only(top:15),
              child: DropdownButton(
                value: _ST,
                items: <String>["","A+", "A-", "B+", "B-", "C+","C-"]
                  .map<DropdownMenuItem<String>>((String value){
                    return DropdownMenuItem<String>(
                      value: value,
                      child: Text(value),
                    );
                  }).toList(),
                onChanged: (String value) =>setState(() {_ST = value;})
              ),
            )
          ),
          Expanded(
            child:TextField(
              controller: _srCtl,
              decoration: InputDecoration(hintText: '积分规则序列号'),
            )
          ),
        ]
      ),
      SizedBox(height:30),
      TextField(
        controller: _keyCtl,
        decoration: InputDecoration(
          hintText: '搜索关键词',
          suffixIcon: IconButton(
            icon: Icon(Icons.search), 
            onPressed: (){
              Map <String, dynamic> fb={'isDpt':_mod.toString(),'flt':jsonEncode(_filters),'st':_ST,'sr':_srCtl.text,'key':_keyCtl.text};
              setState(() {
                _trl=0;
              });
              ruleQuery(fb);
              FocusScope.of(context).requestFocus(FocusNode());
            }
          ),
          border: OutlineInputBorder()
        ),
      ),
      SizedBox(height:30),
    ]
  );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('成峰积分 － 积分规则奖扣',style:TextStyle(fontSize:16)),
        centerTitle: true,
        actions: [
          Row(
            children: <Widget>[
              FlatButton(
                onPressed: () async {
                  final storage = new FlutterSecureStorage();
                  await storage.deleteAll();
                  Navigator.pushReplacementNamed(context, '/login');
                }, 
                child: Text('退出', style:TextStyle(color:Colors.white)),
              )
            ],
          ),
        ],
      ),
      
      body:SingleChildScrollView(
        child: Column(
          children: <Widget>[
            filter(),
            Container(
              padding: EdgeInsets.all(10),
              child: ListView.builder(
                physics: NeverScrollableScrollPhysics(),
                itemCount: _rules.length,
                shrinkWrap: true,
                itemBuilder: (BuildContext context, int index) {
                  Color color=Colors.grey[200], fcolor=Colors.black;
                  if(_trl==_rules[index].id) {
                    color=Colors.red;
                    fcolor=Colors.white;
                  }
                  return Container(
                    width: MediaQuery.of(context).size.width,
                    padding: const EdgeInsets.fromLTRB(0, 10, 0, 10),
                    child: Card(
                      color: color,
                      child: InkWell(
                        onTap: (){
                          setState(() {
                            _trl=_rules[index].id;
                            _rules= _rules.sublist(index,index+1);
                          });
                        },
                        splashColor: Colors.white.withAlpha(80),
                        child: Padding(
                          padding: const EdgeInsets.all(10.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children:<Widget>[
                              Text('序列号：${_rules[index].serial}', style: TextStyle(color: fcolor)),
                              Text('奖扣分：${_rules[index].classify}${_rules[index].score}', style: TextStyle(color: fcolor)),
                              Text(_rules[index].description, style: TextStyle(color: fcolor)),
                            ]
                          ),
                        ),
                      ),
                    ),
                  );
                }
              ),
            ),

            Container(
              width: MediaQuery.of(context).size.width,
              padding: const EdgeInsets.all(15),
              child: RaisedButton(
                onPressed: (){
                  for(int i=0; i<_rules.length; i++){
                    if(_rules[i].id==_trl){
                      Navigator.pop(context, {'score':_rules[i].score.toString(),
                      'classify':_rules[i].classify,
                      'refer':'R','rid':_rules[i].id.toString()});
                    }                      
                  }
                },
                color: Colors.blue,
                child: Text('提 报', style: TextStyle(fontSize: 16,color: Colors.white)),
              ),
            )
          ],
        ),
      ),
    );
  }
}