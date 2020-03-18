import 'package:cfapi/pages/widgets/ruleProposal.dart';
import 'package:cfapi/services/rule.dart';
import 'package:flutter/material.dart';
import 'package:cfapi/pages/widgets/findPenson.dart';

import 'adminProposal.dart';
class ScoreProposal extends StatefulWidget {
  ScoreProposal({Key key}) : super(key: key);
  @override
  _ScoreProposalState createState() => _ScoreProposalState();
}

class _ScoreProposalState extends State<ScoreProposal> {

  void nextStep(bool isRule) async{
    if(isRule){
      Rule rule = await Navigator.push(
        context,
        MaterialPageRoute(
          builder: (BuildContext context) => RuleProposal(),
        ),
      );

      if (rule != null) {
        Scaffold.of(context).showSnackBar(
          SnackBar(
            content: Text("get a rule for you"),
            backgroundColor: Colors.green,
          ),
        );
      }
    }else{
      await Navigator.push(
        context,
        MaterialPageRoute(
          builder: (BuildContext context) => AdminProposal(),
        ),
      );

    }
  }
  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Container(
        padding: EdgeInsets.all(8.0),
        child: Column(
          children: <Widget>[
            FindPenson(),
            SizedBox(height:40.0),
            TextField(
              maxLines: 4,
              keyboardType: TextInputType.multiline,
              decoration:InputDecoration(
                hintText: '描述',
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