import 'authentication.dart';

class Person{
  final int id;
  final String name;
  final String dept;

  Person(this.id,this.name,this.dept);
  Person.fromJson(Map<String, dynamic> json):
      id= json['id'],
      name = json['name'],
      dept = json ['dept'];

  static Future<List<Person>> browse() async {
    Map result= await http('get','persons');
    if(result['error']==0){
      List<Person> Persons= result['lst'].map((json) => Person.fromJson(json)).cast<Person>().toList();
      return Persons;
    }
  }

}