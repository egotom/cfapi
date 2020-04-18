import 'package:cfapi/services/score.dart';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class proposalDetail extends StatelessWidget {

  final Score score; 
  proposalDetail(this.score);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('成峰积分 － 奖扣详情',style:TextStyle(fontSize:16)),
        centerTitle: true,
        actions: [
          Row(
            children: <Widget>[
              FlatButton(
                onPressed: () async {
                  final storage = FlutterSecureStorage();
                  await storage.deleteAll();
                  Navigator.pushReplacementNamed(context, '/login');
                }, 
                child: Text('退出', style:TextStyle(color:Colors.white)),
              )
            ],
          ),
        ],
      ),
      body: Center(child: Column(
        children: <Widget>[
          Text('提交：${score.pname}'),
          Text('奖扣对象：${score.tname}'),
          Text('奖扣：${score.classify} ${score.score}'),
          Text(score.description),          
          Text(score.rule),
          Text(score.create_at),
          Text(score.state)
        ],
      )),
    );
  }
}