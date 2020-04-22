import 'dart:convert';
import 'ruleProposal.dart';
import 'package:cfapi/services/person.dart';
import 'package:flutter/material.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:provider/provider.dart';
//import 'package:cfapi/pages/widgets/findPenson.dart';

import 'adminProposal.dart';
class ScoreProposal extends StatefulWidget {
  ScoreProposal({Key key}) : super(key: key);
  @override
  _ScoreProposalState createState() => _ScoreProposalState();
}

class _ScoreProposalState extends State<ScoreProposal> {
  User _user;
  List<String> _suggestions=[];
  List<String> _peoples=[];
  final TextEditingController _ppCtl = TextEditingController();
  final TextEditingController _cmCtl = TextEditingController();
  void sugLoading() async{
    List<Person> pps=await Person.browse();    
    setState(() {
      _suggestions= pps.map((p)=>p.name).toList();
    });
  }

  @override
  void initState() {
    sugLoading();  
    _user=Provider.of<User>(context, listen: false);  
    _peoples.add(_user.name);
    super.initState();
  }
  void post(Map<String,dynamic> data) async{
    Map result= await http('post','proposal', data:data);
    Scaffold.of(context).showSnackBar(
      SnackBar(content: Text(result['msg'],style:TextStyle(color:Colors.white)),
        backgroundColor: Colors.green,
      ),
    );
  }

  void nextStep(bool isRule) async{
    String cmt=_cmCtl.text.trim();
    if(_peoples.length<1){
      Scaffold.of(context).showSnackBar(
          SnackBar(
            content: Text("填写奖扣对象。",style:TextStyle(color:Colors.red) ),
            backgroundColor: Colors.yellow,
          ),
        );
      return ;
    }
    if(cmt.length<3){
      Scaffold.of(context).showSnackBar(
        SnackBar(
          content: Text("填写正确的奖扣说明。",style:TextStyle(color:Colors.red) ),
          backgroundColor: Colors.yellow,
        ),
      );
      return ;
    }   
    Map <String, dynamic> rts=null;
    if(isRule){
      rts = await Navigator.push(context,
        MaterialPageRoute(
          builder: (BuildContext context) => RuleProposal(),
        ),
      );      
    }else{
      rts=await Navigator.push(context,
        MaterialPageRoute(
          builder: (BuildContext context) => AdminProposal(),
        ),
      );
    }
    if(rts!=null){
      rts['description']=cmt;
      rts['targets'] = jsonEncode(_peoples);
      post(rts);
    }   
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Container(
        padding: EdgeInsets.all(8.0),
        child: Column(
          children: <Widget>[
            TextField(
              controller: _ppCtl,
              decoration: InputDecoration(
                hintText:'添加奖扣对象',    
                suffixIcon: IconButton(
                  icon: Icon(Icons.group_add), 
                  onPressed: (){
                    String name=_ppCtl.text.trim();
                    _ppCtl.text="";
                    if(name!=''){                 
                      setState(() {
                        _peoples.add(name);
                      });
                    }                    
                  }
                ) ,
                border: OutlineInputBorder()
              ),
            ),
            SizedBox(height:20.0),

            Wrap(
              spacing: 8.0, // gap between adjacent chips
              runSpacing: 4.0, 
              children:_peoples.map((String item)=>
                Chip(
                  label: Text(item),
                  deleteIconColor: Colors.red,
                  onDeleted: () {
                    setState(() {
                      _peoples.removeWhere((String name) {
                        return name == item;
                      });
                    });
                  },
                )
              ).toList()
            ),
            SizedBox(height:40.0),
            TextField(
              maxLines: 4,
              keyboardType: TextInputType.multiline,
              controller: _cmCtl,
              decoration:InputDecoration(
                hintText: '奖扣说明',
                border: OutlineInputBorder(),
              )
            ),
            SizedBox(height:60),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: <Widget>[
                  Expanded(
                    child: RaisedButton(              
                      onPressed: ()=>nextStep(false),
                      color: Colors.blue,
                      child: Text('权限审核',style: TextStyle(fontSize: 16,color: Colors.white)),
                    ),
                  ),
                  SizedBox(width:20),
                  Expanded(
                    child: RaisedButton(
                      onPressed: ()=>nextStep(true),
                      color: Colors.blue,
                      child: Text('积分规则',style: TextStyle(fontSize: 16,color: Colors.white)),
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}