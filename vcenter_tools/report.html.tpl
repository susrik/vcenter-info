<head>
<title>virtual machines</title>
</head>
<h1>virtual machines</h1>
<table>
<thead>
<tr>
<th>datacenter</th>
<th>name</th>
<th>state</th>
<th>annotation</th>
</tr>
</thead>
{% for vm in vms %}
<tr>
<td>{{ vm.datacenter }}</td>
<td>{{ vm.name }}</td>
<td>{{ vm.state }}</td>
<td>{{ vm.annotation }}</td>
</tr>
{% endfor %}
</table>
</html>