import 'authentication.dart';

class Rule{
  final int id;
  final int score;
  final String classify;
  final String serial;
  final String department;
  final String property;
  final String description;

  Rule(this.id,this.score,this.classify,this.serial,this.department,this.property,this.description);

  Rule.fromJson(Map<String, dynamic> json):
      id= json['id'],
      score = json['score'],
      classify = json ['classify'],
      serial= json ['serial'],
      department= json ['department'],
      property= json ['property'],
      description= json ['description'];

  static Future<List<Rule>> browse() async {
    Map result= await http('get','rules');
    if(result['error']==0){
      List<Rule> rules= result['lst'].map((json) => Rule.fromJson(json)).cast<Rule>().toList();
      return rules;
    }
  }
}