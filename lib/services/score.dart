import 'package:cfapi/services/authentication.dart';
class Score {
  final int id;
  final int score;
  final String tname;
  final String pname;
  final String state;
  final String rule;  
  final String classify;
  final String refer;
  final String description;
  final String create_at;

  Score({this.id,this.score,this.tname,this.pname, this.state, this.rule,this.classify,this.refer,this.description,this.create_at});

  factory Score.fromJson(Map<String, dynamic> json){
    return Score(
      id: json['id'],
      score : json['score'],
      tname : json['tname'],
      pname : json['pname'],
      state : json['state'],
      rule:json['rule'],
      classify:json['classify'],
      refer:json['refer'],
      description:json['description'],
      create_at:json['create_at']
    );
  }

  static Future<List> browse({List<DateTime> range ,int page}) async {
    Map result= (range!=null)?await http('post','score',data:{'range':range.toString()}) :await http('get','score');
    if(result['error']==0){
      List scores=result['lst'].map((json) => Score.fromJson(json)).toList();
      return scores;
    }
  }
  static Future<List> progress({List<DateTime> range ,int page}) async {
    Map result= (range!=null)?await http('post','progress',data:{'range':range.toString()}) :await http('get','progress');
    if(result['error']==0){
      List scores=result['lst'].map((json) => Score.fromJson(json)).toList();
      return scores;
    }
  }
  static Future<bool> remove(int id) async {
    Map result= await http('del','progress/${id}');
    if(result['error']==0){
      return true;
    }
    return false;
  }
}
