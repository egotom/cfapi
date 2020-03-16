import 'package:cfapi/services/authentication.dart';
class Score {
  final int id;
  final int score;
  final String name;
  final String rule;  
  final String classify;
  final String refer;
  final String description;
  final String create_at;

  Score({this.id,this.score,this.name,this.rule,this.classify,this.refer,this.description,this.create_at});

  factory Score.fromJson(Map<String, dynamic> json){
    return Score(
      id: json['id'],
      score : json['score'],
      name : json ['name'],
      rule:json ['rule'],
      classify:json ['classify'],
      refer:json ['refer'],
      description:json ['description'],
      create_at:json ['create_at']
    );
  }

  static Future<List> browse({List<DateTime> range ,int page}) async {
    Map result= (range!=null)?await http('post','score',data:{'range':range.toString()}) :await http('get','score');
    if(result['error']==0){
      List scores=result['lst'].map((json) => Score.fromJson(json)).toList();
      return scores;
    }
  }
}
