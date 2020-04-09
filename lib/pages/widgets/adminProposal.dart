import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AdminProposal extends StatefulWidget {
  @override
  _AdminProposalState createState() => _AdminProposalState();
}

class _AdminProposalState extends State<AdminProposal> {
  bool _lty=true;
  String _ST='B+';
  final TextEditingController _scCtl = TextEditingController();
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('成峰积分 － 权限奖扣',style:TextStyle(fontSize:16)),
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

      body: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          children:<Widget>[
            SwitchListTile(
              inactiveThumbColor: Colors.red,
              title: _lty?
                Text('有奖券',style: TextStyle(color:Colors.blue,fontWeight:FontWeight.bold)):
                Text('无奖券',style: TextStyle(color:Colors.red,fontWeight:FontWeight.bold)),
              value: _lty,
              onChanged: (bool value) { setState(() { _lty = value; }); },
              secondary: _lty? 
                Icon(Icons.filter_1, color: Colors.blue):
                Icon(Icons.filter_none, color: Colors.red),
            ),
            SizedBox(height:30),
            Container(
              width: MediaQuery.of(context).size.width,
              child: DropdownButton(
                value: _ST,
                items: <String>["A+", "A-", "B+", "B-", "C+","C-"]
                  .map<DropdownMenuItem<String>>((String value){
                    return DropdownMenuItem<String>(
                      value: value,
                      child: Text(value),
                    );
                  }).toList(),
                onChanged: (String value) =>setState(() {_ST = value;})
              ),
            ),
            SizedBox(height:30),
            TextField(
              controller: _scCtl,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(hintText: '分值'),
            ),
            SizedBox(height:60),
            Container(
              width: MediaQuery.of(context).size.width,
              child:RaisedButton(              
                onPressed: () {
                  int _score=double.parse(_scCtl.text).round();
                  Navigator.pop(context, {'score':_score.toString(),'classify':_ST,'refer':_lty?'C':'F'});
                },
                color: Colors.blue,
                child: Text('提 报',style: TextStyle(fontSize: 16,color: Colors.white)),
              ),
            ),
          ]
        ),
      ),
    );
  }
}