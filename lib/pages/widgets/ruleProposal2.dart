import 'package:cfapi/pages/widgets/selectCard.dart';
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

  void ruleLoading() async{
    List<Rule> rules=await Rule.browse();
    setState(() {
      _rules= rules;
    });
    print(rules);
  }

  @override
  void initState() {
    ruleLoading();
    super.initState();
  }

  final List<String> dept=["管理人员","市场部","客管部","客服部","技术部","计划部","采购部","仓库","发货","金工部","电机","下线","电气部","装泵","电焊","工程部","质量部","IT部","人力部","后勤部","财务部","统计部","招商部"];
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
        child: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Column(
            children:<Widget>[            
              SwitchListTile(
                inactiveThumbColor: Colors.red,
                title: _mod?
                  Text('按部门搜索',style: TextStyle(color:Colors.blue,fontWeight:FontWeight.bold)):
                  Text('按积分规则属性搜索',style: TextStyle(color:Colors.red,fontWeight:FontWeight.bold)),
                value: _mod,
                onChanged: (bool value) { setState(() { _mod = value;}); },
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
                      decoration: InputDecoration(hintText: '积分规则序列号'),
                    )
                  ),
                ]
              ),
              SizedBox(height:30),
              //TextField(
              //  decoration: InputDecoration(
              //    hintText: '搜索',
              //    prefixIcon: Icon(Icons.search),
              //    border: OutlineInputBorder()
              //  ),
              //),
              //SizedBox(height:30),
              Container(
                width: MediaQuery.of(context).size.width,
                height: 900,
                child: CustomScrollView(
                  slivers: <Widget>[
                    SliverPersistentHeader(
                      floating: true,
                      delegate:CustomSliverHeaderDelegate(
                        expandedHeight: 80.0,
                        child: TextField(
                          decoration: InputDecoration(
                            hintText: '搜索',
                            prefixIcon: Icon(Icons.search),
                            border: OutlineInputBorder()
                          ),
                        ),
                      ),
                    ),

                    SliverFixedExtentList(
                      itemExtent: 50.0,
                      delegate: SliverChildBuilderDelegate(
                        (BuildContext context, int index) {
                          return Container(
                            width: MediaQuery.of(context).size.width,
                            padding: const EdgeInsets.fromLTRB(0, 10, 0, 10),
                            child: Card(
                              color: Colors.amber,
                              child: InkWell(
                                onTap: (){},
                                splashColor: Colors.white.withAlpha(80),
                                child: Padding(
                                  padding: const EdgeInsets.all(10.0),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children:<Widget>[
                                      Text(_rules[index].serial),
                                      Text('${_rules[index].classify}${_rules[index].score}'),
                                      Text(_rules[index].description),
                                    ]
                                  ),
                                ),
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  ]
                ),
              ),
            ]
          ),
        ),
      )
    );
  }
}

class CustomSliverHeaderDelegate extends SliverPersistentHeaderDelegate {
  final double expandedHeight;
  final Widget child;

  CustomSliverHeaderDelegate({
    @required this.expandedHeight,
    @required this.child,
  });

  @override
  Widget build(BuildContext context, double shrinkOffset, bool overlapsContent) {
    return child;
  }

  @override
  double get maxExtent => expandedHeight;

  @override
  double get minExtent => expandedHeight;

  @override
  bool shouldRebuild(SliverPersistentHeaderDelegate oldDelegate) {
    return true;
  }
}
