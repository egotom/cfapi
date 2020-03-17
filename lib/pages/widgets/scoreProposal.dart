import 'package:flutter/material.dart';
import 'package:cfapi/pages/widgets/findPenson.dart';
class ScoreProposal extends StatefulWidget {
  ScoreProposal({Key key}) : super(key: key);
  @override
  _ScoreProposalState createState() => _ScoreProposalState();
}

class _ScoreProposalState extends State<ScoreProposal> {
  bool _mod=true, _lty=true;
  int _score=0;
  String _ST='B+';

  @override
  void initState() {
    super.initState();
  }

  Container rule=Container(
    child: Text('data'),
  );
  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Container(
        padding: EdgeInsets.all(8.0),
        child: Column(
          children: <Widget>[
            FindPenson(),
            SizedBox(height:20.0),
            TextField(
              maxLines: 4,
              keyboardType: TextInputType.multiline,
              decoration:InputDecoration(
                hintText: '描述',
                border: OutlineInputBorder(),
              )
            ),
            SwitchListTile(
              inactiveThumbColor: Colors.red,
              title: _mod?
                Text('奖扣权限',style: TextStyle(color:Colors.blue,fontWeight:FontWeight.bold)):
                Text('奖扣规则',style: TextStyle(color:Colors.red,fontWeight:FontWeight.bold)),
              value: _mod,
              onChanged: (bool value) { setState(() { _mod = value; }); },
              secondary: _mod? 
                Icon(Icons.assignment_ind,color: Colors.blue):
                Icon(Icons.assignment,color: Colors.red),
            ),
            SizedBox(height:20.0),

            
            _mod? Column(
              children: <Widget>[
                SwitchListTile(
                  inactiveThumbColor: Colors.red,
                  title: _lty?
                    Text('默认奖券模式',style: TextStyle(color:Colors.blue,fontWeight:FontWeight.bold)):
                    Text('无奖券',style: TextStyle(color:Colors.red,fontWeight:FontWeight.bold)),
                  value: _lty,
                  onChanged: (bool value) { setState(() { _lty = value; }); },
                  secondary: _lty? 
                    Icon(Icons.filter_1, color: Colors.blue):
                    Icon(Icons.filter_none, color: Colors.red),
                ),
                Row(
                  children: <Widget>[
                    SizedBox(height:20.0),
                    Container(
                      width: MediaQuery.of(context).size.width*4/10,
                      padding: EdgeInsets.only(top:15),
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
                    SizedBox(height:20.0),
                    Container(
                      width: MediaQuery.of(context).size.width*4/10,
                      child: TextField(
                        keyboardType: TextInputType.number,
                        decoration: InputDecoration(hintText: '分值'),
                      ),
                    ),
                  ],
                ),
              ],
            ): rule,
            SizedBox(height:60),
            Container(
              width: MediaQuery.of(context).size.width,
              child:RaisedButton(              
                onPressed: () {},
                color: Colors.blue,
                child: Text('确认',style: TextStyle(fontSize: 16,color: Colors.white)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}